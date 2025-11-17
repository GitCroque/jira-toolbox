#!/usr/bin/env python3
"""
Script de gestion des projets Jira Cloud
Permet de lister, créer, modifier, archiver des projets
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class ProjectManager:
    """Gestionnaire de projets Jira"""

    def __init__(self, client: JiraClient):
        self.client = client

    def list_projects(self, expand: List[str] = None) -> List[Dict]:
        """Liste tous les projets"""
        params = {}
        if expand:
            params['expand'] = ','.join(expand)

        projects = self.client.get_paginated('project/search', params=params)
        return projects

    def get_project(self, project_key: str) -> Dict:
        """Récupère les détails d'un projet"""
        return self.client.get(f'project/{project_key}')

    def get_project_components(self, project_key: str) -> List[Dict]:
        """Récupère les composants d'un projet"""
        return self.client.get(f'project/{project_key}/components') or []

    def get_project_versions(self, project_key: str) -> List[Dict]:
        """Récupère les versions d'un projet"""
        return self.client.get_paginated(f'project/{project_key}/versions')

    def get_project_issues_stats(self, project_key: str) -> Dict:
        """Statistiques sur les issues d'un projet"""
        # Recherche JQL pour compter les issues
        jql_queries = {
            'total': f'project = {project_key}',
            'open': f'project = {project_key} AND status != Done',
            'in_progress': f'project = {project_key} AND status = "In Progress"',
            'done': f'project = {project_key} AND status = Done'
        }

        stats = {}
        for stat_name, jql in jql_queries.items():
            result = self.client.get('search', params={
                'jql': jql,
                'maxResults': 0,
                'fields': 'id'
            })
            stats[stat_name] = result.get('total', 0) if result else 0

        return stats

    def create_project(self, data: Dict) -> Dict:
        """
        Crée un nouveau projet

        Args:
            data: Données du projet (name, key, projectTypeKey, lead, description, etc.)
        """
        return self.client.post('project', data=data)

    def update_project(self, project_key: str, data: Dict) -> Dict:
        """Met à jour un projet"""
        return self.client.put(f'project/{project_key}', data=data)

    def archive_project(self, project_key: str) -> bool:
        """Archive un projet"""
        return self.client.post(f'project/{project_key}/archive')

    def restore_project(self, project_key: str) -> bool:
        """Restaure un projet archivé"""
        return self.client.post(f'project/{project_key}/restore')

    def get_project_roles_assignments(self, project_key: str) -> Dict:
        """Récupère les assignations de rôles d'un projet"""
        roles = self.client.get(f'project/{project_key}/role')

        role_assignments = {}
        if roles:
            for role_name, role_url in roles.items():
                role_id = role_url.split('/')[-1]
                role_info = self.client.get(f'project/{project_key}/role/{role_id}')

                if role_info:
                    role_assignments[role_name] = {
                        'actors': role_info.get('actors', []),
                        'count': len(role_info.get('actors', []))
                    }

        return role_assignments

    def export_project_config(self, project_key: str, filename: str):
        """Exporte la configuration complète d'un projet"""
        project = self.get_project(project_key)
        components = self.get_project_components(project_key)
        versions = self.get_project_versions(project_key)
        roles = self.get_project_roles_assignments(project_key)
        stats = self.get_project_issues_stats(project_key)

        config = {
            'project': project,
            'components': components,
            'versions': versions,
            'roles': roles,
            'statistics': stats,
            'export_date': datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✓ Configuration exportée vers {filename}")


def main():
    parser = argparse.ArgumentParser(description='Gestion des projets Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Liste des projets
    list_parser = subparsers.add_parser('list', help='Lister tous les projets')
    list_parser.add_argument('--format', choices=['json', 'table'], default='table',
                            help='Format de sortie')
    list_parser.add_argument('--expand', nargs='*',
                            help='Champs à développer (description, lead, etc.)')

    # Détails d'un projet
    get_parser = subparsers.add_parser('get', help='Détails d\'un projet')
    get_parser.add_argument('project_key', help='Clé du projet')
    get_parser.add_argument('--format', choices=['json', 'summary'], default='summary')

    # Composants d'un projet
    components_parser = subparsers.add_parser('components', help='Composants d\'un projet')
    components_parser.add_argument('project_key', help='Clé du projet')

    # Versions d'un projet
    versions_parser = subparsers.add_parser('versions', help='Versions d\'un projet')
    versions_parser.add_argument('project_key', help='Clé du projet')

    # Statistiques d'un projet
    stats_parser = subparsers.add_parser('stats', help='Statistiques d\'un projet')
    stats_parser.add_argument('project_key', help='Clé du projet')

    # Export de configuration
    export_parser = subparsers.add_parser('export', help='Exporter la configuration d\'un projet')
    export_parser.add_argument('project_key', help='Clé du projet')
    export_parser.add_argument('--output', help='Fichier de sortie', required=True)

    # Archiver un projet
    archive_parser = subparsers.add_parser('archive', help='Archiver un projet')
    archive_parser.add_argument('project_key', help='Clé du projet')
    archive_parser.add_argument('--confirm', action='store_true',
                               help='Confirmer l\'archivage')

    # Restaurer un projet
    restore_parser = subparsers.add_parser('restore', help='Restaurer un projet archivé')
    restore_parser.add_argument('project_key', help='Clé du projet')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        manager = ProjectManager(client)

        if args.command == 'list':
            projects = manager.list_projects(expand=args.expand)

            if args.format == 'json':
                print(json.dumps(projects, indent=2, ensure_ascii=False))
            else:
                print(f"\n{'Clé':<15} {'Nom':<40} {'Type':<20} {'Chef de projet':<30}")
                print("-" * 110)
                for proj in projects:
                    lead = proj.get('lead', {}).get('displayName', 'N/A') if proj.get('lead') else 'N/A'
                    print(f"{proj.get('key', ''):<15} "
                          f"{proj.get('name', ''):<40} "
                          f"{proj.get('projectTypeKey', ''):<20} "
                          f"{lead:<30}")
                print(f"\nTotal: {len(projects)} projets")

        elif args.command == 'get':
            project = manager.get_project(args.project_key)

            if not project:
                print(f"Projet {args.project_key} non trouvé", file=sys.stderr)
                sys.exit(1)

            if args.format == 'json':
                print(json.dumps(project, indent=2, ensure_ascii=False))
            else:
                print(f"\n=== PROJET {project.get('key')} ===")
                print(f"Nom: {project.get('name')}")
                print(f"Description: {project.get('description', 'N/A')}")
                print(f"Type: {project.get('projectTypeKey')}")
                print(f"Style: {project.get('style')}")
                lead = project.get('lead', {})
                if lead:
                    print(f"Chef de projet: {lead.get('displayName')} ({lead.get('emailAddress', 'N/A')})")
                print(f"URL: {project.get('self')}")

        elif args.command == 'components':
            components = manager.get_project_components(args.project_key)
            print(f"\n=== COMPOSANTS DU PROJET {args.project_key} ===")
            for comp in components:
                print(f"\n  • {comp.get('name')}")
                print(f"    ID: {comp.get('id')}")
                if comp.get('description'):
                    print(f"    Description: {comp.get('description')}")
                if comp.get('lead'):
                    print(f"    Responsable: {comp.get('lead', {}).get('displayName')}")
            print(f"\nTotal: {len(components)} composants")

        elif args.command == 'versions':
            versions = manager.get_project_versions(args.project_key)
            print(f"\n=== VERSIONS DU PROJET {args.project_key} ===")
            for ver in versions:
                status = []
                if ver.get('released'):
                    status.append('RELEASED')
                if ver.get('archived'):
                    status.append('ARCHIVED')
                status_str = f" [{', '.join(status)}]" if status else ""

                print(f"\n  • {ver.get('name')}{status_str}")
                print(f"    ID: {ver.get('id')}")
                if ver.get('description'):
                    print(f"    Description: {ver.get('description')}")
                if ver.get('releaseDate'):
                    print(f"    Date de release: {ver.get('releaseDate')}")
            print(f"\nTotal: {len(versions)} versions")

        elif args.command == 'stats':
            stats = manager.get_project_issues_stats(args.project_key)
            print(f"\n=== STATISTIQUES DU PROJET {args.project_key} ===")
            print(f"Total issues: {stats['total']}")
            print(f"Ouvertes: {stats['open']}")
            print(f"En cours: {stats['in_progress']}")
            print(f"Terminées: {stats['done']}")

            if stats['total'] > 0:
                done_pct = (stats['done'] / stats['total']) * 100
                print(f"\nProgression: {done_pct:.1f}% complété")

        elif args.command == 'export':
            manager.export_project_config(args.project_key, args.output)

        elif args.command == 'archive':
            if not args.confirm:
                response = input(f"⚠ Confirmer l'archivage du projet {args.project_key} ? (oui/non): ")
                if response.lower() not in ['oui', 'o', 'yes', 'y']:
                    print("Archivage annulé")
                    return

            result = manager.archive_project(args.project_key)
            if result:
                print(f"✓ Projet {args.project_key} archivé")
            else:
                print(f"✗ Échec de l'archivage", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'restore':
            result = manager.restore_project(args.project_key)
            if result:
                print(f"✓ Projet {args.project_key} restauré")
            else:
                print(f"✗ Échec de la restauration", file=sys.stderr)
                sys.exit(1)

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
