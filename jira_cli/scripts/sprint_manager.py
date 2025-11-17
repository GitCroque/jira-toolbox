#!/usr/bin/env python3
"""
Script de gestion avancée des sprints Jira Cloud
Permet de créer, modifier, démarrer, terminer des sprints
Gérer les issues, analyser la vélocité et le burndown
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class SprintManager:
    """Gestionnaire de sprints Jira"""

    def __init__(self, client: JiraClient):
        self.client = client

    def get_board(self, board_id: int) -> Dict:
        """Récupère les détails d'un board"""
        return self.client.get(f'board/{board_id}')

    def list_boards(self, project_key: str = None) -> List[Dict]:
        """Liste tous les boards"""
        params = {}
        if project_key:
            params['projectKeyOrId'] = project_key

        return self.client.get_paginated('board', params=params)

    def create_sprint(self, board_id: int, name: str, start_date: str = None,
                     end_date: str = None, goal: str = None) -> Dict:
        """
        Crée un nouveau sprint

        Args:
            board_id: ID du board
            name: Nom du sprint
            start_date: Date de début (format ISO 8601)
            end_date: Date de fin (format ISO 8601)
            goal: Objectif du sprint
        """
        sprint_data = {
            'name': name,
            'originBoardId': board_id
        }

        if start_date:
            sprint_data['startDate'] = start_date
        if end_date:
            sprint_data['endDate'] = end_date
        if goal:
            sprint_data['goal'] = goal

        return self.client.post('sprint', data=sprint_data)

    def get_sprint(self, sprint_id: int) -> Dict:
        """Récupère les détails d'un sprint"""
        return self.client.get(f'sprint/{sprint_id}')

    def update_sprint(self, sprint_id: int, name: str = None, start_date: str = None,
                     end_date: str = None, goal: str = None, state: str = None) -> Dict:
        """
        Met à jour un sprint

        Args:
            sprint_id: ID du sprint
            name: Nouveau nom
            start_date: Nouvelle date de début
            end_date: Nouvelle date de fin
            goal: Nouvel objectif
            state: Nouvel état (future, active, closed)
        """
        update_data = {}

        if name:
            update_data['name'] = name
        if start_date:
            update_data['startDate'] = start_date
        if end_date:
            update_data['endDate'] = end_date
        if goal:
            update_data['goal'] = goal
        if state:
            update_data['state'] = state

        return self.client.post(f'sprint/{sprint_id}', data=update_data)

    def delete_sprint(self, sprint_id: int) -> bool:
        """Supprime un sprint"""
        return self.client.delete(f'sprint/{sprint_id}')

    def start_sprint(self, sprint_id: int, start_date: str = None, end_date: str = None) -> Dict:
        """
        Démarre un sprint

        Args:
            sprint_id: ID du sprint
            start_date: Date de début (par défaut: maintenant)
            end_date: Date de fin (par défaut: +2 semaines)
        """
        if not start_date:
            start_date = datetime.now().isoformat()

        if not end_date:
            end = datetime.now() + timedelta(weeks=2)
            end_date = end.isoformat()

        return self.update_sprint(sprint_id, start_date=start_date,
                                 end_date=end_date, state='active')

    def close_sprint(self, sprint_id: int) -> Dict:
        """Termine un sprint"""
        return self.update_sprint(sprint_id, state='closed')

    def list_sprints(self, board_id: int, state: str = None) -> List[Dict]:
        """
        Liste les sprints d'un board

        Args:
            board_id: ID du board
            state: Filtrer par état (future, active, closed)
        """
        params = {}
        if state:
            params['state'] = state

        return self.client.get_paginated(f'board/{board_id}/sprint', params=params)

    def get_sprint_issues(self, sprint_id: int, jql: str = None) -> List[Dict]:
        """Récupère les issues d'un sprint"""
        params = {}
        if jql:
            params['jql'] = jql

        result = self.client.get_paginated(f'sprint/{sprint_id}/issue', params=params)
        return result

    def add_issues_to_sprint(self, sprint_id: int, issue_keys: List[str]) -> bool:
        """Ajoute des issues à un sprint"""
        data = {'issues': issue_keys}
        result = self.client.post(f'sprint/{sprint_id}/issue', data=data)
        return result is not None

    def move_issues_to_sprint(self, sprint_id: int, issue_keys: List[str]) -> bool:
        """Déplace des issues vers un sprint (retire du sprint actuel)"""
        return self.add_issues_to_sprint(sprint_id, issue_keys)

    def remove_issues_from_sprint(self, issue_keys: List[str]) -> bool:
        """Retire des issues d'un sprint (vers le backlog)"""
        # Pour retirer des issues d'un sprint, on les assigne au sprint 0 (backlog)
        for issue_key in issue_keys:
            update_data = {
                'fields': {
                    'sprint': None
                }
            }
            result = self.client.put(f'issue/{issue_key}', data=update_data)
            if not result:
                return False
        return True

    def get_sprint_report(self, sprint_id: int) -> Dict:
        """Génère un rapport de sprint"""
        sprint = self.get_sprint(sprint_id)
        issues = self.get_sprint_issues(sprint_id)

        # Analyse des issues
        total = len(issues)
        by_status = defaultdict(int)
        by_type = defaultdict(int)
        story_points = 0
        completed_points = 0

        for issue in issues:
            fields = issue.get('fields', {})

            # Statut
            status = fields.get('status', {}).get('name', 'Unknown')
            by_status[status] += 1

            # Type
            issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
            by_type[issue_type] += 1

            # Story points (custom field - peut varier)
            points = fields.get('customfield_10016')  # Champ story points courant
            if points:
                try:
                    story_points += float(points)
                    if status.lower() in ['done', 'closed', 'resolved']:
                        completed_points += float(points)
                except:
                    pass

        completion_rate = (completed_points / story_points * 100) if story_points > 0 else 0

        return {
            'sprint': sprint,
            'total_issues': total,
            'by_status': dict(by_status),
            'by_type': dict(by_type),
            'story_points': story_points,
            'completed_points': completed_points,
            'completion_rate': round(completion_rate, 2),
            'velocity': completed_points,
            'report_date': datetime.now().isoformat()
        }

    def calculate_velocity(self, board_id: int, num_sprints: int = 5) -> Dict:
        """
        Calcule la vélocité moyenne sur les derniers sprints

        Args:
            board_id: ID du board
            num_sprints: Nombre de sprints à analyser
        """
        sprints = self.list_sprints(board_id, state='closed')
        recent_sprints = sorted(sprints, key=lambda s: s.get('endDate', ''), reverse=True)[:num_sprints]

        velocities = []
        sprint_details = []

        for sprint in recent_sprints:
            report = self.get_sprint_report(sprint['id'])
            velocity = report['velocity']
            velocities.append(velocity)

            sprint_details.append({
                'id': sprint['id'],
                'name': sprint['name'],
                'velocity': velocity,
                'completion_rate': report['completion_rate']
            })

        avg_velocity = sum(velocities) / len(velocities) if velocities else 0

        return {
            'board_id': board_id,
            'sprints_analyzed': len(recent_sprints),
            'average_velocity': round(avg_velocity, 2),
            'velocities': velocities,
            'sprint_details': sprint_details,
            'analysis_date': datetime.now().isoformat()
        }

    def get_burndown_data(self, sprint_id: int) -> Dict:
        """
        Génère les données pour un burndown chart

        Note: Nécessite l'accès aux données historiques
        Cette fonction fournit une approximation basée sur les données actuelles
        """
        sprint = self.get_sprint(sprint_id)
        issues = self.get_sprint_issues(sprint_id)

        start_date = sprint.get('startDate')
        end_date = sprint.get('endDate')

        if not start_date or not end_date:
            return {
                'error': 'Sprint n\'a pas de dates définies',
                'sprint_id': sprint_id
            }

        # Calculer le travail restant
        total_points = 0
        remaining_points = 0

        for issue in issues:
            fields = issue.get('fields', {})
            points = fields.get('customfield_10016')  # Story points

            if points:
                try:
                    points_val = float(points)
                    total_points += points_val

                    status = fields.get('status', {}).get('name', '').lower()
                    if status not in ['done', 'closed', 'resolved']:
                        remaining_points += points_val
                except:
                    pass

        completed_points = total_points - remaining_points
        completion_percentage = (completed_points / total_points * 100) if total_points > 0 else 0

        return {
            'sprint_id': sprint_id,
            'sprint_name': sprint.get('name'),
            'start_date': start_date,
            'end_date': end_date,
            'total_points': total_points,
            'completed_points': completed_points,
            'remaining_points': remaining_points,
            'completion_percentage': round(completion_percentage, 2),
            'is_on_track': remaining_points == 0 or sprint.get('state') == 'closed'
        }

    def export_sprint_summary(self, sprint_id: int, filename: str):
        """Exporte un résumé de sprint en JSON"""
        sprint = self.get_sprint(sprint_id)
        report = self.get_sprint_report(sprint_id)
        burndown = self.get_burndown_data(sprint_id)
        issues = self.get_sprint_issues(sprint_id)

        summary = {
            'sprint': sprint,
            'report': report,
            'burndown': burndown,
            'issues': [{
                'key': i['key'],
                'summary': i.get('fields', {}).get('summary'),
                'status': i.get('fields', {}).get('status', {}).get('name'),
                'assignee': i.get('fields', {}).get('assignee', {}).get('displayName')
                    if i.get('fields', {}).get('assignee') else None
            } for i in issues]
        }

        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"✓ Résumé du sprint exporté vers {filename}")


def main():
    parser = argparse.ArgumentParser(description='Gestion avancée des sprints Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Lister les boards
    boards_parser = subparsers.add_parser('boards', help='Lister les boards')
    boards_parser.add_argument('--project', help='Filtrer par projet')

    # Créer un sprint
    create_parser = subparsers.add_parser('create', help='Créer un sprint')
    create_parser.add_argument('board_id', type=int, help='ID du board')
    create_parser.add_argument('name', help='Nom du sprint')
    create_parser.add_argument('--start', help='Date de début (ISO 8601)')
    create_parser.add_argument('--end', help='Date de fin (ISO 8601)')
    create_parser.add_argument('--goal', help='Objectif du sprint')

    # Voir un sprint
    get_parser = subparsers.add_parser('get', help='Voir un sprint')
    get_parser.add_argument('sprint_id', type=int, help='ID du sprint')

    # Mettre à jour un sprint
    update_parser = subparsers.add_parser('update', help='Mettre à jour un sprint')
    update_parser.add_argument('sprint_id', type=int, help='ID du sprint')
    update_parser.add_argument('--name', help='Nouveau nom')
    update_parser.add_argument('--start', help='Nouvelle date de début')
    update_parser.add_argument('--end', help='Nouvelle date de fin')
    update_parser.add_argument('--goal', help='Nouvel objectif')

    # Supprimer un sprint
    delete_parser = subparsers.add_parser('delete', help='Supprimer un sprint')
    delete_parser.add_argument('sprint_id', type=int, help='ID du sprint')
    delete_parser.add_argument('--confirm', action='store_true', help='Confirmer')

    # Démarrer un sprint
    start_parser = subparsers.add_parser('start', help='Démarrer un sprint')
    start_parser.add_argument('sprint_id', type=int, help='ID du sprint')
    start_parser.add_argument('--start', help='Date de début')
    start_parser.add_argument('--end', help='Date de fin')

    # Terminer un sprint
    close_parser = subparsers.add_parser('close', help='Terminer un sprint')
    close_parser.add_argument('sprint_id', type=int, help='ID du sprint')

    # Lister les sprints
    list_parser = subparsers.add_parser('list', help='Lister les sprints d\'un board')
    list_parser.add_argument('board_id', type=int, help='ID du board')
    list_parser.add_argument('--state', choices=['future', 'active', 'closed'],
                            help='Filtrer par état')

    # Issues d'un sprint
    issues_parser = subparsers.add_parser('issues', help='Lister les issues d\'un sprint')
    issues_parser.add_argument('sprint_id', type=int, help='ID du sprint')
    issues_parser.add_argument('--jql', help='Filtre JQL additionnel')

    # Ajouter des issues
    add_issues_parser = subparsers.add_parser('add-issues', help='Ajouter des issues au sprint')
    add_issues_parser.add_argument('sprint_id', type=int, help='ID du sprint')
    add_issues_parser.add_argument('issue_keys', nargs='+', help='Clés des issues')

    # Retirer des issues
    remove_issues_parser = subparsers.add_parser('remove-issues',
                                                help='Retirer des issues du sprint')
    remove_issues_parser.add_argument('issue_keys', nargs='+', help='Clés des issues')

    # Déplacer des issues
    move_issues_parser = subparsers.add_parser('move-issues',
                                              help='Déplacer des issues vers un sprint')
    move_issues_parser.add_argument('sprint_id', type=int, help='ID du sprint cible')
    move_issues_parser.add_argument('issue_keys', nargs='+', help='Clés des issues')

    # Rapport de sprint
    report_parser = subparsers.add_parser('report', help='Rapport de sprint')
    report_parser.add_argument('sprint_id', type=int, help='ID du sprint')
    report_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Vélocité
    velocity_parser = subparsers.add_parser('velocity', help='Calculer la vélocité moyenne')
    velocity_parser.add_argument('board_id', type=int, help='ID du board')
    velocity_parser.add_argument('--sprints', type=int, default=5,
                                help='Nombre de sprints à analyser')

    # Burndown
    burndown_parser = subparsers.add_parser('burndown', help='Données de burndown')
    burndown_parser.add_argument('sprint_id', type=int, help='ID du sprint')

    # Export
    export_parser = subparsers.add_parser('export', help='Exporter un résumé de sprint')
    export_parser.add_argument('sprint_id', type=int, help='ID du sprint')
    export_parser.add_argument('filename', help='Nom du fichier')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        manager = SprintManager(client)

        if args.command == 'boards':
            boards = manager.list_boards(args.project)
            print(f"\n{'ID':<10} {'Nom':<40} {'Type':<20}")
            print("-" * 70)
            for board in boards:
                print(f"{board['id']:<10} {board['name']:<40} {board['type']:<20}")
            print(f"\nTotal: {len(boards)} boards")

        elif args.command == 'create':
            sprint = manager.create_sprint(
                board_id=args.board_id,
                name=args.name,
                start_date=args.start,
                end_date=args.end,
                goal=args.goal
            )
            if sprint:
                print(f"✓ Sprint créé: {sprint['name']} (ID: {sprint['id']})")
            else:
                print("✗ Échec de la création", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'get':
            sprint = manager.get_sprint(args.sprint_id)
            if sprint:
                print(json.dumps(sprint, indent=2, ensure_ascii=False))
            else:
                print(f"Sprint {args.sprint_id} non trouvé", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'update':
            sprint = manager.update_sprint(
                sprint_id=args.sprint_id,
                name=args.name,
                start_date=args.start,
                end_date=args.end,
                goal=args.goal
            )
            if sprint:
                print(f"✓ Sprint {args.sprint_id} mis à jour")
            else:
                print("✗ Échec de la mise à jour", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'delete':
            if not args.confirm:
                response = input(f"⚠ Confirmer la suppression du sprint {args.sprint_id} ? (oui/non): ")
                if response.lower() not in ['oui', 'o', 'yes', 'y']:
                    print("Suppression annulée")
                    return

            if manager.delete_sprint(args.sprint_id):
                print(f"✓ Sprint {args.sprint_id} supprimé")
            else:
                print("✗ Échec de la suppression", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'start':
            sprint = manager.start_sprint(args.sprint_id, args.start, args.end)
            if sprint:
                print(f"✓ Sprint {args.sprint_id} démarré")
                print(f"  Début: {sprint.get('startDate')}")
                print(f"  Fin: {sprint.get('endDate')}")
            else:
                print("✗ Échec du démarrage", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'close':
            sprint = manager.close_sprint(args.sprint_id)
            if sprint:
                print(f"✓ Sprint {args.sprint_id} terminé")
            else:
                print("✗ Échec de la clôture", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'list':
            sprints = manager.list_sprints(args.board_id, args.state)
            print(f"\n{'ID':<10} {'Nom':<40} {'État':<15} {'Dates'}")
            print("-" * 100)
            for sprint in sprints:
                dates = f"{sprint.get('startDate', 'N/A')[:10]} - {sprint.get('endDate', 'N/A')[:10]}"
                print(f"{sprint['id']:<10} {sprint['name']:<40} "
                      f"{sprint['state']:<15} {dates}")
            print(f"\nTotal: {len(sprints)} sprints")

        elif args.command == 'issues':
            issues = manager.get_sprint_issues(args.sprint_id, args.jql)
            print(f"\nIssues du sprint {args.sprint_id}:")
            for issue in issues:
                fields = issue.get('fields', {})
                status = fields.get('status', {}).get('name', 'Unknown')
                print(f"  • {issue['key']}: {fields.get('summary', '')} [{status}]")
            print(f"\nTotal: {len(issues)} issues")

        elif args.command == 'add-issues':
            if manager.add_issues_to_sprint(args.sprint_id, args.issue_keys):
                print(f"✓ {len(args.issue_keys)} issue(s) ajoutée(s) au sprint {args.sprint_id}")
            else:
                print("✗ Échec de l'ajout", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'remove-issues':
            if manager.remove_issues_from_sprint(args.issue_keys):
                print(f"✓ {len(args.issue_keys)} issue(s) retirée(s) du sprint")
            else:
                print("✗ Échec du retrait", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'move-issues':
            if manager.move_issues_to_sprint(args.sprint_id, args.issue_keys):
                print(f"✓ {len(args.issue_keys)} issue(s) déplacée(s) vers le sprint {args.sprint_id}")
            else:
                print("✗ Échec du déplacement", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'report':
            report = manager.get_sprint_report(args.sprint_id)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"✓ Rapport exporté vers {args.output}")
            else:
                print(f"\n=== RAPPORT SPRINT: {report['sprint']['name']} ===")
                print(f"État: {report['sprint']['state']}")
                print(f"Total issues: {report['total_issues']}")
                print(f"Story points: {report['story_points']}")
                print(f"Points complétés: {report['completed_points']}")
                print(f"Taux de complétion: {report['completion_rate']}%")
                print(f"Vélocité: {report['velocity']}")
                print(f"\nPar statut:")
                for status, count in report['by_status'].items():
                    print(f"  • {status}: {count}")
                print(f"\nPar type:")
                for itype, count in report['by_type'].items():
                    print(f"  • {itype}: {count}")

        elif args.command == 'velocity':
            velocity_data = manager.calculate_velocity(args.board_id, args.sprints)
            print(f"\n=== ANALYSE DE VÉLOCITÉ ===")
            print(f"Board ID: {velocity_data['board_id']}")
            print(f"Sprints analysés: {velocity_data['sprints_analyzed']}")
            print(f"Vélocité moyenne: {velocity_data['average_velocity']} points")
            print(f"\nDétails par sprint:")
            for sprint in velocity_data['sprint_details']:
                print(f"  • {sprint['name']}: {sprint['velocity']} points "
                      f"({sprint['completion_rate']}% complété)")

        elif args.command == 'burndown':
            burndown = manager.get_burndown_data(args.sprint_id)
            if 'error' in burndown:
                print(f"✗ {burndown['error']}", file=sys.stderr)
                sys.exit(1)

            print(f"\n=== BURNDOWN CHART: {burndown['sprint_name']} ===")
            print(f"Période: {burndown['start_date'][:10]} - {burndown['end_date'][:10]}")
            print(f"Total points: {burndown['total_points']}")
            print(f"Points complétés: {burndown['completed_points']}")
            print(f"Points restants: {burndown['remaining_points']}")
            print(f"Complétion: {burndown['completion_percentage']}%")
            print(f"Sur la bonne voie: {'✓' if burndown['is_on_track'] else '✗'}")

        elif args.command == 'export':
            manager.export_sprint_summary(args.sprint_id, args.filename)

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
