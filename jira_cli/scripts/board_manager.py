#!/usr/bin/env python3
"""
Script de gestion des boards (tableaux) Jira Cloud
Permet de lister, créer, configurer des boards
Gérer les colonnes, swimlanes, filtres
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class BoardManager:
    """Gestionnaire de boards Jira"""

    def __init__(self, client: JiraClient):
        self.client = client

    def list_boards(self, project_key: str = None, board_type: str = None,
                   name: str = None) -> List[Dict]:
        """
        Liste tous les boards

        Args:
            project_key: Filtrer par projet
            board_type: Type de board (scrum, kanban, simple)
            name: Filtrer par nom
        """
        params = {}
        if project_key:
            params['projectKeyOrId'] = project_key
        if board_type:
            params['type'] = board_type
        if name:
            params['name'] = name

        return self.client.get_paginated('board', params=params)

    def get_board(self, board_id: int) -> Dict:
        """Récupère les détails d'un board"""
        return self.client.get(f'board/{board_id}')

    def create_board(self, name: str, board_type: str, filter_id: int = None,
                    project_key: str = None) -> Dict:
        """
        Crée un nouveau board

        Args:
            name: Nom du board
            board_type: Type (scrum, kanban)
            filter_id: ID du filtre (optionnel)
            project_key: Clé du projet (optionnel)
        """
        board_data = {
            'name': name,
            'type': board_type
        }

        if filter_id:
            board_data['filterId'] = filter_id

        if project_key:
            # Récupérer l'ID du projet
            project = self.client.get(f'project/{project_key}')
            if project:
                board_data['location'] = {
                    'type': 'project',
                    'projectKeyOrId': project_key
                }

        return self.client.post('board', data=board_data)

    def delete_board(self, board_id: int) -> bool:
        """Supprime un board"""
        return self.client.delete(f'board/{board_id}')

    def get_board_configuration(self, board_id: int) -> Dict:
        """Récupère la configuration d'un board"""
        return self.client.get(f'board/{board_id}/configuration')

    def get_board_filter(self, board_id: int) -> Dict:
        """Récupère le filtre associé à un board"""
        config = self.get_board_configuration(board_id)
        if config and 'filter' in config:
            filter_id = config['filter']['id']
            return self.client.get(f'filter/{filter_id}')
        return None

    def get_board_columns(self, board_id: int) -> List[Dict]:
        """Récupère les colonnes d'un board"""
        config = self.get_board_configuration(board_id)
        if config and 'columnConfig' in config:
            return config['columnConfig'].get('columns', [])
        return []

    def get_board_issues(self, board_id: int, jql: str = None,
                        max_results: int = 50) -> List[Dict]:
        """Récupère les issues d'un board"""
        params = {'maxResults': max_results}
        if jql:
            params['jql'] = jql

        return self.client.get_paginated(f'board/{board_id}/issue', params=params)

    def get_board_backlog(self, board_id: int) -> List[Dict]:
        """Récupère le backlog d'un board"""
        return self.client.get_paginated(f'board/{board_id}/backlog')

    def get_board_sprints(self, board_id: int, state: str = None) -> List[Dict]:
        """
        Récupère les sprints d'un board

        Args:
            board_id: ID du board
            state: Filtrer par état (future, active, closed)
        """
        params = {}
        if state:
            params['state'] = state

        return self.client.get_paginated(f'board/{board_id}/sprint', params=params)

    def get_board_epics(self, board_id: int) -> List[Dict]:
        """Récupère les epics d'un board"""
        return self.client.get_paginated(f'board/{board_id}/epic')

    def get_board_versions(self, board_id: int, released: bool = None) -> List[Dict]:
        """
        Récupère les versions d'un board

        Args:
            board_id: ID du board
            released: Filtrer par statut de release
        """
        params = {}
        if released is not None:
            params['released'] = 'true' if released else 'false'

        return self.client.get_paginated(f'board/{board_id}/version', params=params)

    def get_board_projects(self, board_id: int) -> List[Dict]:
        """Récupère les projets associés à un board"""
        # Utiliser la configuration pour trouver le projet
        config = self.get_board_configuration(board_id)
        if not config:
            return []

        # Extraire les projets depuis le filtre
        board_filter = self.get_board_filter(board_id)
        if board_filter:
            # Parser le JQL pour trouver les projets (approximation)
            jql = board_filter.get('jql', '')
            # Cette approche est simplifiée - en production, il faudrait un parser JQL complet
            if 'project' in jql.lower():
                # Récupérer les issues du board pour identifier les projets
                issues = self.get_board_issues(board_id, max_results=10)
                project_keys = set()
                for issue in issues:
                    project_key = issue.get('fields', {}).get('project', {}).get('key')
                    if project_key:
                        project_keys.add(project_key)

                # Récupérer les détails des projets
                projects = []
                for key in project_keys:
                    project = self.client.get(f'project/{key}')
                    if project:
                        projects.append(project)
                return projects

        return []

    def get_board_summary(self, board_id: int) -> Dict:
        """Génère un résumé complet d'un board"""
        board = self.get_board(board_id)
        config = self.get_board_configuration(board_id)
        columns = self.get_board_columns(board_id)
        issues = self.get_board_issues(board_id)

        # Compter les issues par colonne (approximation via status)
        issues_by_column = {}
        for col in columns:
            col_name = col.get('name')
            # Compter les issues avec un statut correspondant
            statuses = [s.get('name') for s in col.get('statuses', [])]
            count = sum(1 for i in issues
                       if i.get('fields', {}).get('status', {}).get('name') in statuses)
            issues_by_column[col_name] = count

        return {
            'board': board,
            'type': board.get('type'),
            'columns': columns,
            'column_count': len(columns),
            'total_issues': len(issues),
            'issues_by_column': issues_by_column,
            'summary_date': datetime.now().isoformat()
        }

    def export_board_config(self, board_id: int, filename: str):
        """Exporte la configuration complète d'un board"""
        board = self.get_board(board_id)
        config = self.get_board_configuration(board_id)
        columns = self.get_board_columns(board_id)
        board_filter = self.get_board_filter(board_id)

        export_data = {
            'board': board,
            'configuration': config,
            'columns': columns,
            'filter': board_filter,
            'export_date': datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Configuration du board exportée vers {filename}")

    def analyze_board_performance(self, board_id: int) -> Dict:
        """Analyse la performance d'un board"""
        issues = self.get_board_issues(board_id, max_results=500)

        # Statistiques
        total_issues = len(issues)
        by_status = {}
        by_priority = {}
        by_assignee = {}

        for issue in issues:
            fields = issue.get('fields', {})

            # Par statut
            status = fields.get('status', {}).get('name', 'Unknown')
            by_status[status] = by_status.get(status, 0) + 1

            # Par priorité
            priority = fields.get('priority', {}).get('name', 'Unknown')
            by_priority[priority] = by_priority.get(priority, 0) + 1

            # Par assigné
            assignee = fields.get('assignee')
            if assignee:
                name = assignee.get('displayName', 'Unknown')
                by_assignee[name] = by_assignee.get(name, 0) + 1
            else:
                by_assignee['Non assigné'] = by_assignee.get('Non assigné', 0) + 1

        return {
            'board_id': board_id,
            'total_issues': total_issues,
            'by_status': by_status,
            'by_priority': by_priority,
            'by_assignee': by_assignee,
            'top_assignees': sorted(by_assignee.items(), key=lambda x: x[1], reverse=True)[:10],
            'analysis_date': datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser(description='Gestion des boards Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Lister les boards
    list_parser = subparsers.add_parser('list', help='Lister les boards')
    list_parser.add_argument('--project', help='Filtrer par projet')
    list_parser.add_argument('--type', choices=['scrum', 'kanban', 'simple'],
                            help='Filtrer par type')
    list_parser.add_argument('--name', help='Filtrer par nom')

    # Voir un board
    get_parser = subparsers.add_parser('get', help='Voir un board')
    get_parser.add_argument('board_id', type=int, help='ID du board')

    # Créer un board
    create_parser = subparsers.add_parser('create', help='Créer un board')
    create_parser.add_argument('name', help='Nom du board')
    create_parser.add_argument('--type', choices=['scrum', 'kanban'], required=True,
                              help='Type de board')
    create_parser.add_argument('--project', help='Clé du projet')
    create_parser.add_argument('--filter', type=int, help='ID du filtre')

    # Supprimer un board
    delete_parser = subparsers.add_parser('delete', help='Supprimer un board')
    delete_parser.add_argument('board_id', type=int, help='ID du board')
    delete_parser.add_argument('--confirm', action='store_true', help='Confirmer')

    # Configuration
    config_parser = subparsers.add_parser('config', help='Configuration d\'un board')
    config_parser.add_argument('board_id', type=int, help='ID du board')

    # Colonnes
    columns_parser = subparsers.add_parser('columns', help='Colonnes d\'un board')
    columns_parser.add_argument('board_id', type=int, help='ID du board')

    # Issues
    issues_parser = subparsers.add_parser('issues', help='Issues d\'un board')
    issues_parser.add_argument('board_id', type=int, help='ID du board')
    issues_parser.add_argument('--jql', help='Filtre JQL')
    issues_parser.add_argument('--max', type=int, default=50, help='Nombre max')

    # Backlog
    backlog_parser = subparsers.add_parser('backlog', help='Backlog d\'un board')
    backlog_parser.add_argument('board_id', type=int, help='ID du board')

    # Sprints
    sprints_parser = subparsers.add_parser('sprints', help='Sprints d\'un board')
    sprints_parser.add_argument('board_id', type=int, help='ID du board')
    sprints_parser.add_argument('--state', choices=['future', 'active', 'closed'],
                               help='Filtrer par état')

    # Epics
    epics_parser = subparsers.add_parser('epics', help='Epics d\'un board')
    epics_parser.add_argument('board_id', type=int, help='ID du board')

    # Versions
    versions_parser = subparsers.add_parser('versions', help='Versions d\'un board')
    versions_parser.add_argument('board_id', type=int, help='ID du board')
    versions_parser.add_argument('--released', action='store_true', help='Seulement released')
    versions_parser.add_argument('--unreleased', action='store_true', help='Seulement unreleased')

    # Résumé
    summary_parser = subparsers.add_parser('summary', help='Résumé d\'un board')
    summary_parser.add_argument('board_id', type=int, help='ID du board')
    summary_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Export
    export_parser = subparsers.add_parser('export', help='Exporter la configuration')
    export_parser.add_argument('board_id', type=int, help='ID du board')
    export_parser.add_argument('filename', help='Fichier de sortie')

    # Analyse
    analyze_parser = subparsers.add_parser('analyze', help='Analyser la performance')
    analyze_parser.add_argument('board_id', type=int, help='ID du board')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        manager = BoardManager(client)

        if args.command == 'list':
            boards = manager.list_boards(args.project, args.type, args.name)
            print(f"\n{'ID':<10} {'Nom':<50} {'Type':<15}")
            print("-" * 75)
            for board in boards:
                print(f"{board['id']:<10} {board['name']:<50} {board['type']:<15}")
            print(f"\nTotal: {len(boards)} boards")

        elif args.command == 'get':
            board = manager.get_board(args.board_id)
            if board:
                print(json.dumps(board, indent=2, ensure_ascii=False))
            else:
                print(f"Board {args.board_id} non trouvé", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'create':
            board = manager.create_board(args.name, args.type, args.filter, args.project)
            if board:
                print(f"✓ Board créé: {board['name']} (ID: {board['id']})")
            else:
                print("✗ Échec de la création", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'delete':
            if not args.confirm:
                response = input(f"⚠ Confirmer la suppression du board {args.board_id} ? (oui/non): ")
                if response.lower() not in ['oui', 'o', 'yes', 'y']:
                    print("Suppression annulée")
                    return

            if manager.delete_board(args.board_id):
                print(f"✓ Board {args.board_id} supprimé")
            else:
                print("✗ Échec de la suppression", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'config':
            config = manager.get_board_configuration(args.board_id)
            if config:
                print(json.dumps(config, indent=2, ensure_ascii=False))
            else:
                print(f"Configuration non trouvée", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'columns':
            columns = manager.get_board_columns(args.board_id)
            print(f"\nColonnes du board {args.board_id}:")
            for i, col in enumerate(columns, 1):
                print(f"\n{i}. {col.get('name')}")
                statuses = col.get('statuses', [])
                if statuses:
                    print(f"   Statuts:")
                    for status in statuses:
                        print(f"     • {status.get('name')}")

        elif args.command == 'issues':
            issues = manager.get_board_issues(args.board_id, args.jql, args.max)
            print(f"\nIssues du board {args.board_id}:")
            for issue in issues:
                fields = issue.get('fields', {})
                status = fields.get('status', {}).get('name', 'Unknown')
                print(f"  • {issue['key']}: {fields.get('summary', '')} [{status}]")
            print(f"\nTotal: {len(issues)} issues")

        elif args.command == 'backlog':
            backlog = manager.get_board_backlog(args.board_id)
            print(f"\nBacklog du board {args.board_id}:")
            for issue in backlog:
                fields = issue.get('fields', {})
                print(f"  • {issue['key']}: {fields.get('summary', '')}")
            print(f"\nTotal: {len(backlog)} issues")

        elif args.command == 'sprints':
            sprints = manager.get_board_sprints(args.board_id, args.state)
            print(f"\nSprints du board {args.board_id}:")
            for sprint in sprints:
                state_indicator = {'future': '⏳', 'active': '🚀', 'closed': '✅'}.get(sprint['state'], '•')
                print(f"  {state_indicator} [{sprint['id']}] {sprint['name']} ({sprint['state']})")
            print(f"\nTotal: {len(sprints)} sprints")

        elif args.command == 'epics':
            epics = manager.get_board_epics(args.board_id)
            print(f"\nEpics du board {args.board_id}:")
            for epic in epics:
                print(f"  • {epic.get('key')}: {epic.get('name')}")
            print(f"\nTotal: {len(epics)} epics")

        elif args.command == 'versions':
            released_filter = None
            if args.released:
                released_filter = True
            elif args.unreleased:
                released_filter = False

            versions = manager.get_board_versions(args.board_id, released_filter)
            print(f"\nVersions du board {args.board_id}:")
            for version in versions:
                released = "✓" if version.get('released') else "○"
                print(f"  {released} {version.get('name')}")
            print(f"\nTotal: {len(versions)} versions")

        elif args.command == 'summary':
            summary = manager.get_board_summary(args.board_id)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                print(f"✓ Résumé exporté vers {args.output}")
            else:
                print(f"\n=== RÉSUMÉ BOARD: {summary['board']['name']} ===")
                print(f"Type: {summary['type']}")
                print(f"Total issues: {summary['total_issues']}")
                print(f"Colonnes ({summary['column_count']}):")
                for col_name, count in summary['issues_by_column'].items():
                    print(f"  • {col_name}: {count} issues")

        elif args.command == 'export':
            manager.export_board_config(args.board_id, args.filename)

        elif args.command == 'analyze':
            analysis = manager.analyze_board_performance(args.board_id)

            print(f"\n=== ANALYSE BOARD {args.board_id} ===")
            print(f"Total issues: {analysis['total_issues']}")
            print(f"\nPar statut:")
            for status, count in analysis['by_status'].items():
                print(f"  • {status}: {count}")
            print(f"\nPar priorité:")
            for priority, count in analysis['by_priority'].items():
                print(f"  • {priority}: {count}")
            print(f"\nTop assignés:")
            for name, count in analysis['top_assignees']:
                print(f"  • {name}: {count} issues")

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
