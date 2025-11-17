#!/usr/bin/env python3
"""
Script de reporting et d'analytique Jira Cloud
Génère des rapports sur l'activité, la performance, les métriques
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class ReportingTool:
    """Outil de reporting Jira"""

    def __init__(self, client: JiraClient):
        self.client = client

    def get_issues_by_jql(self, jql: str, fields: List[str] = None) -> List[Dict]:
        """Recherche d'issues par JQL"""
        params = {
            'jql': jql,
            'maxResults': 100
        }
        if fields:
            params['fields'] = ','.join(fields)

        return self.client.get_paginated('search', params=params)

    def generate_project_report(self, project_key: str) -> Dict:
        """Génère un rapport complet pour un projet"""
        jql = f'project = {project_key}'
        issues = self.get_issues_by_jql(
            jql,
            fields=['status', 'issuetype', 'priority', 'assignee', 'created', 'updated', 'resolutiondate']
        )

        # Analyse par statut
        by_status = Counter()
        by_type = Counter()
        by_priority = Counter()
        by_assignee = Counter()

        for issue in issues:
            fields = issue.get('fields', {})

            status = fields.get('status', {}).get('name', 'Unknown')
            by_status[status] += 1

            issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
            by_type[issue_type] += 1

            priority = fields.get('priority', {}).get('name', 'Unknown')
            by_priority[priority] += 1

            assignee = fields.get('assignee')
            if assignee:
                by_assignee[assignee.get('displayName', 'Unassigned')] += 1
            else:
                by_assignee['Non assigné'] += 1

        return {
            'project_key': project_key,
            'total_issues': len(issues),
            'by_status': dict(by_status),
            'by_type': dict(by_type),
            'by_priority': dict(by_priority),
            'by_assignee': dict(by_assignee),
            'report_date': datetime.now().isoformat()
        }

    def generate_user_activity_report(self, account_id: str, days: int = 30) -> Dict:
        """Rapport d'activité d'un utilisateur"""
        date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        # Issues créées
        jql_created = f'creator = "{account_id}" AND created >= {date_from}'
        created_issues = self.get_issues_by_jql(jql_created, fields=['key', 'summary', 'created'])

        # Issues assignées
        jql_assigned = f'assignee = "{account_id}" AND updated >= {date_from}'
        assigned_issues = self.get_issues_by_jql(jql_assigned, fields=['key', 'summary', 'status'])

        # Issues résolues
        jql_resolved = f'assignee = "{account_id}" AND resolved >= {date_from}'
        resolved_issues = self.get_issues_by_jql(jql_resolved, fields=['key', 'summary', 'resolutiondate'])

        return {
            'account_id': account_id,
            'period_days': days,
            'issues_created': len(created_issues),
            'issues_assigned': len(assigned_issues),
            'issues_resolved': len(resolved_issues),
            'created_list': [{'key': i.get('key'), 'summary': i.get('fields', {}).get('summary')}
                           for i in created_issues[:10]],  # Top 10
            'report_date': datetime.now().isoformat()
        }

    def generate_sprint_report(self, board_id: int) -> Dict:
        """Rapport sur les sprints d'un board"""
        # Récupérer les sprints
        sprints = self.client.get_paginated(f'board/{board_id}/sprint')

        sprint_data = []
        for sprint in sprints[:5]:  # 5 derniers sprints
            sprint_id = sprint.get('id')
            sprint_issues = self.client.get_paginated(f'sprint/{sprint_id}/issue')

            # Analyse des issues du sprint
            completed = sum(1 for i in sprint_issues
                          if i.get('fields', {}).get('status', {}).get('name') == 'Done')

            sprint_data.append({
                'id': sprint_id,
                'name': sprint.get('name'),
                'state': sprint.get('state'),
                'startDate': sprint.get('startDate'),
                'endDate': sprint.get('endDate'),
                'total_issues': len(sprint_issues),
                'completed_issues': completed,
                'completion_rate': (completed / len(sprint_issues) * 100) if sprint_issues else 0
            })

        return {
            'board_id': board_id,
            'sprints': sprint_data,
            'report_date': datetime.now().isoformat()
        }

    def generate_sla_report(self, project_key: str) -> Dict:
        """Rapport sur les SLA (temps de résolution, etc.)"""
        # Issues créées dans les 30 derniers jours
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        jql = f'project = {project_key} AND created >= {date_from}'

        issues = self.get_issues_by_jql(
            jql,
            fields=['created', 'resolutiondate', 'status', 'priority']
        )

        resolution_times = []
        open_issues_age = []

        for issue in issues:
            fields = issue.get('fields', {})
            created = fields.get('created')
            resolved = fields.get('resolutiondate')

            if created:
                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))

                if resolved:
                    resolved_dt = datetime.fromisoformat(resolved.replace('Z', '+00:00'))
                    resolution_time = (resolved_dt - created_dt).total_seconds() / 3600  # heures
                    resolution_times.append(resolution_time)
                else:
                    # Issue encore ouverte
                    age = (datetime.now() - created_dt.replace(tzinfo=None)).total_seconds() / 3600
                    open_issues_age.append(age)

        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        avg_age = sum(open_issues_age) / len(open_issues_age) if open_issues_age else 0

        return {
            'project_key': project_key,
            'period_days': 30,
            'total_issues': len(issues),
            'resolved_issues': len(resolution_times),
            'open_issues': len(open_issues_age),
            'avg_resolution_time_hours': round(avg_resolution, 2),
            'avg_open_issue_age_hours': round(avg_age, 2),
            'report_date': datetime.now().isoformat()
        }

    def generate_dashboard_summary(self) -> Dict:
        """Résumé global pour un dashboard"""
        # Récupérer tous les projets
        projects = self.client.get_paginated('project/search')

        total_issues = 0
        total_open = 0
        total_in_progress = 0
        total_done = 0

        for project in projects[:20]:  # Limiter à 20 projets pour la perf
            project_key = project.get('key')

            # Compter les issues
            result = self.client.get('search', params={
                'jql': f'project = {project_key}',
                'maxResults': 0
            })
            if result:
                total_issues += result.get('total', 0)

            # Issues ouvertes
            result = self.client.get('search', params={
                'jql': f'project = {project_key} AND status != Done',
                'maxResults': 0
            })
            if result:
                total_open += result.get('total', 0)

        return {
            'total_projects': len(projects),
            'total_issues': total_issues,
            'open_issues': total_open,
            'report_date': datetime.now().isoformat()
        }

    def export_csv_report(self, project_key: str, filename: str):
        """Exporte un rapport en CSV"""
        import csv

        jql = f'project = {project_key}'
        issues = self.get_issues_by_jql(
            jql,
            fields=['summary', 'status', 'issuetype', 'priority', 'assignee', 'created', 'updated']
        )

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Key', 'Summary', 'Type', 'Status', 'Priority', 'Assignee', 'Created', 'Updated'
            ])
            writer.writeheader()

            for issue in issues:
                fields = issue.get('fields', {})
                assignee = fields.get('assignee')

                writer.writerow({
                    'Key': issue.get('key'),
                    'Summary': fields.get('summary', ''),
                    'Type': fields.get('issuetype', {}).get('name', ''),
                    'Status': fields.get('status', {}).get('name', ''),
                    'Priority': fields.get('priority', {}).get('name', ''),
                    'Assignee': assignee.get('displayName') if assignee else 'Non assigné',
                    'Created': fields.get('created', ''),
                    'Updated': fields.get('updated', '')
                })

        print(f"✓ {len(issues)} issues exportées vers {filename}")


def main():
    parser = argparse.ArgumentParser(description='Reporting et analytique Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Rapport de projet
    project_parser = subparsers.add_parser('project', help='Rapport d\'un projet')
    project_parser.add_argument('project_key', help='Clé du projet')
    project_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Activité utilisateur
    user_parser = subparsers.add_parser('user', help='Rapport d\'activité utilisateur')
    user_parser.add_argument('account_id', help='Account ID de l\'utilisateur')
    user_parser.add_argument('--days', type=int, default=30, help='Période en jours')
    user_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Rapport SLA
    sla_parser = subparsers.add_parser('sla', help='Rapport SLA d\'un projet')
    sla_parser.add_argument('project_key', help='Clé du projet')
    sla_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Dashboard
    dashboard_parser = subparsers.add_parser('dashboard', help='Résumé global')
    dashboard_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Export CSV
    csv_parser = subparsers.add_parser('export-csv', help='Exporter les issues en CSV')
    csv_parser.add_argument('project_key', help='Clé du projet')
    csv_parser.add_argument('filename', help='Nom du fichier CSV')

    # Recherche JQL personnalisée
    jql_parser = subparsers.add_parser('jql', help='Recherche JQL personnalisée')
    jql_parser.add_argument('query', help='Requête JQL')
    jql_parser.add_argument('--fields', nargs='*', help='Champs à récupérer')
    jql_parser.add_argument('--output', help='Fichier de sortie JSON')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        reporting = ReportingTool(client)

        if args.command == 'project':
            report = reporting.generate_project_report(args.project_key)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"✓ Rapport exporté vers {args.output}")
            else:
                print(f"\n=== RAPPORT DU PROJET {args.project_key} ===")
                print(f"Total issues: {report['total_issues']}")
                print(f"\nPar statut:")
                for status, count in report['by_status'].items():
                    print(f"  • {status}: {count}")
                print(f"\nPar type:")
                for itype, count in report['by_type'].items():
                    print(f"  • {itype}: {count}")
                print(f"\nPar priorité:")
                for priority, count in report['by_priority'].items():
                    print(f"  • {priority}: {count}")
                print(f"\nTop assignés:")
                sorted_assignees = sorted(report['by_assignee'].items(),
                                        key=lambda x: x[1], reverse=True)[:10]
                for assignee, count in sorted_assignees:
                    print(f"  • {assignee}: {count}")

        elif args.command == 'user':
            report = reporting.generate_user_activity_report(args.account_id, args.days)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"✓ Rapport exporté vers {args.output}")
            else:
                print(f"\n=== ACTIVITÉ UTILISATEUR ({args.days} derniers jours) ===")
                print(f"Issues créées: {report['issues_created']}")
                print(f"Issues assignées: {report['issues_assigned']}")
                print(f"Issues résolues: {report['issues_resolved']}")

                if report['created_list']:
                    print(f"\nDernières issues créées:")
                    for issue in report['created_list']:
                        print(f"  • {issue['key']}: {issue['summary']}")

        elif args.command == 'sla':
            report = reporting.generate_sla_report(args.project_key)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"✓ Rapport exporté vers {args.output}")
            else:
                print(f"\n=== RAPPORT SLA - {args.project_key} ===")
                print(f"Période: {report['period_days']} jours")
                print(f"Total issues: {report['total_issues']}")
                print(f"Issues résolues: {report['resolved_issues']}")
                print(f"Issues ouvertes: {report['open_issues']}")
                print(f"\nTemps moyen de résolution: {report['avg_resolution_time_hours']:.1f} heures")
                print(f"Âge moyen des issues ouvertes: {report['avg_open_issue_age_hours']:.1f} heures")

        elif args.command == 'dashboard':
            report = reporting.generate_dashboard_summary()

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"✓ Rapport exporté vers {args.output}")
            else:
                print(f"\n=== DASHBOARD JIRA ===")
                print(f"Total projets: {report['total_projects']}")
                print(f"Total issues: {report['total_issues']}")
                print(f"Issues ouvertes: {report['open_issues']}")

        elif args.command == 'export-csv':
            reporting.export_csv_report(args.project_key, args.filename)

        elif args.command == 'jql':
            issues = reporting.get_issues_by_jql(args.query, fields=args.fields)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(issues, f, indent=2, ensure_ascii=False)
                print(f"✓ {len(issues)} issues exportées vers {args.output}")
            else:
                print(json.dumps(issues, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
