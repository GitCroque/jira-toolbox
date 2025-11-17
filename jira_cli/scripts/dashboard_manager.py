#!/usr/bin/env python3
"""
Script de gestion des dashboards et filtres Jira Cloud
Permet de créer, modifier, partager des dashboards et filtres
Gérer les favoris et la propriété
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class DashboardFilterManager:
    """Gestionnaire de dashboards et filtres Jira"""

    def __init__(self, client: JiraClient):
        self.client = client

    # === DASHBOARDS ===

    def list_dashboards(self, max_results: int = 50) -> List[Dict]:
        """Liste tous les dashboards"""
        return self.client.get_paginated('dashboard', params={'maxResults': max_results})

    def get_dashboard(self, dashboard_id: str) -> Dict:
        """Récupère les détails d'un dashboard"""
        return self.client.get(f'dashboard/{dashboard_id}')

    def search_dashboards(self, dashboard_name: str = None, owner: str = None) -> List[Dict]:
        """
        Recherche des dashboards

        Args:
            dashboard_name: Nom du dashboard
            owner: Account ID du propriétaire
        """
        params = {}
        if dashboard_name:
            params['dashboardName'] = dashboard_name
        if owner:
            params['owner'] = owner

        result = self.client.get('dashboard/search', params=params)
        return result.get('values', []) if result else []

    def copy_dashboard(self, dashboard_id: str, name: str, description: str = None) -> Dict:
        """
        Copie un dashboard

        Args:
            dashboard_id: ID du dashboard source
            name: Nom du nouveau dashboard
            description: Description (optionnel)
        """
        copy_data = {
            'name': name
        }
        if description:
            copy_data['description'] = description

        return self.client.post(f'dashboard/{dashboard_id}/copy', data=copy_data)

    def get_dashboard_gadgets(self, dashboard_id: str) -> List[Dict]:
        """Récupère les gadgets d'un dashboard"""
        dashboard = self.get_dashboard(dashboard_id)
        return dashboard.get('gadgets', []) if dashboard else []

    # === FILTRES ===

    def list_filters(self, expand: str = None) -> List[Dict]:
        """Liste tous les filtres accessibles"""
        params = {}
        if expand:
            params['expand'] = expand

        return self.client.get_paginated('filter', params=params)

    def get_filter(self, filter_id: int) -> Dict:
        """Récupère les détails d'un filtre"""
        return self.client.get(f'filter/{filter_id}')

    def search_filters(self, filter_name: str = None, account_id: str = None,
                      group_name: str = None, favourite: bool = None) -> List[Dict]:
        """
        Recherche des filtres

        Args:
            filter_name: Nom du filtre
            account_id: Propriétaire
            group_name: Groupe
            favourite: Seulement les favoris
        """
        params = {}
        if filter_name:
            params['filterName'] = filter_name
        if account_id:
            params['accountId'] = account_id
        if group_name:
            params['groupname'] = group_name
        if favourite is not None:
            params['favourite'] = 'true' if favourite else 'false'

        result = self.client.get('filter/search', params=params)
        return result.get('values', []) if result else []

    def create_filter(self, name: str, jql: str, description: str = None,
                     favourite: bool = False) -> Dict:
        """
        Crée un nouveau filtre

        Args:
            name: Nom du filtre
            jql: Requête JQL
            description: Description
            favourite: Ajouter aux favoris
        """
        filter_data = {
            'name': name,
            'jql': jql,
            'favourite': favourite
        }

        if description:
            filter_data['description'] = description

        return self.client.post('filter', data=filter_data)

    def update_filter(self, filter_id: int, name: str = None, jql: str = None,
                     description: str = None, favourite: bool = None) -> Dict:
        """Met à jour un filtre"""
        filter_data = {}

        if name:
            filter_data['name'] = name
        if jql:
            filter_data['jql'] = jql
        if description:
            filter_data['description'] = description
        if favourite is not None:
            filter_data['favourite'] = favourite

        return self.client.put(f'filter/{filter_id}', data=filter_data)

    def delete_filter(self, filter_id: int) -> bool:
        """Supprime un filtre"""
        return self.client.delete(f'filter/{filter_id}')

    def get_filter_columns(self, filter_id: int) -> List[str]:
        """Récupère les colonnes d'un filtre"""
        result = self.client.get(f'filter/{filter_id}/columns')
        return result if result else []

    def set_filter_columns(self, filter_id: int, columns: List[str]) -> List[str]:
        """Définit les colonnes d'un filtre"""
        return self.client.put(f'filter/{filter_id}/columns', data=columns)

    def get_favourite_filters(self) -> List[Dict]:
        """Récupère les filtres favoris de l'utilisateur connecté"""
        return self.client.get('filter/favourite') or []

    def add_filter_to_favourites(self, filter_id: int) -> Dict:
        """Ajoute un filtre aux favoris"""
        # Note: L'API Jira utilise le endpoint de mise à jour
        return self.update_filter(filter_id, favourite=True)

    def remove_filter_from_favourites(self, filter_id: int) -> Dict:
        """Retire un filtre des favoris"""
        return self.update_filter(filter_id, favourite=False)

    def change_filter_owner(self, filter_id: int, account_id: str) -> Dict:
        """
        Change le propriétaire d'un filtre

        Args:
            filter_id: ID du filtre
            account_id: Account ID du nouveau propriétaire
        """
        return self.client.put(f'filter/{filter_id}/owner', data={'accountId': account_id})

    def get_filter_share_permissions(self, filter_id: int) -> List[Dict]:
        """Récupère les permissions de partage d'un filtre"""
        result = self.client.get(f'filter/{filter_id}/permission')
        return result if result else []

    def add_filter_share_permission(self, filter_id: int, permission_type: str,
                                    project_id: str = None, group_name: str = None,
                                    role_id: str = None) -> Dict:
        """
        Ajoute une permission de partage à un filtre

        Args:
            filter_id: ID du filtre
            permission_type: Type (group, project, projectRole, global, authenticated, loggedin)
            project_id: ID du projet (pour project/projectRole)
            group_name: Nom du groupe (pour group)
            role_id: ID du rôle (pour projectRole)
        """
        permission_data = {
            'type': permission_type
        }

        if project_id:
            permission_data['project'] = {'id': project_id}
        if group_name:
            permission_data['group'] = {'name': group_name}
        if role_id:
            permission_data['role'] = {'id': role_id}

        return self.client.post(f'filter/{filter_id}/permission', data=permission_data)

    def delete_filter_share_permission(self, filter_id: int, permission_id: int) -> bool:
        """Supprime une permission de partage"""
        return self.client.delete(f'filter/{filter_id}/permission/{permission_id}')

    # === UTILITAIRES ===

    def export_filter_results(self, filter_id: int, filename: str, format: str = 'json'):
        """
        Exporte les résultats d'un filtre

        Args:
            filter_id: ID du filtre
            filename: Fichier de sortie
            format: Format (json, csv)
        """
        filter_obj = self.get_filter(filter_id)
        if not filter_obj:
            print(f"Filtre {filter_id} non trouvé", file=sys.stderr)
            return

        jql = filter_obj.get('jql')

        # Exécuter la recherche
        issues = self.client.get_paginated('search', params={'jql': jql})

        if format == 'json':
            with open(filename, 'w') as f:
                json.dump({
                    'filter': filter_obj,
                    'issues': issues,
                    'total': len(issues),
                    'export_date': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            print(f"✓ {len(issues)} issues exportées vers {filename}")

        elif format == 'csv':
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if not issues:
                    print("Aucune issue trouvée")
                    return

                writer = csv.DictWriter(f, fieldnames=['key', 'summary', 'status', 'assignee', 'priority'])
                writer.writeheader()

                for issue in issues:
                    fields = issue.get('fields', {})
                    assignee = fields.get('assignee')

                    writer.writerow({
                        'key': issue['key'],
                        'summary': fields.get('summary', ''),
                        'status': fields.get('status', {}).get('name', ''),
                        'assignee': assignee.get('displayName') if assignee else 'Non assigné',
                        'priority': fields.get('priority', {}).get('name', '')
                    })

            print(f"✓ {len(issues)} issues exportées vers {filename}")

    def clone_filter(self, filter_id: int, new_name: str) -> Dict:
        """Clone un filtre"""
        original = self.get_filter(filter_id)
        if not original:
            return None

        return self.create_filter(
            name=new_name,
            jql=original.get('jql'),
            description=f"Clone de {original.get('name')}",
            favourite=False
        )


def main():
    parser = argparse.ArgumentParser(description='Gestion des dashboards et filtres Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # === DASHBOARDS ===

    dash_list_parser = subparsers.add_parser('dashboard-list', help='Lister les dashboards')
    dash_list_parser.add_argument('--max', type=int, default=50, help='Nombre maximum')

    dash_get_parser = subparsers.add_parser('dashboard-get', help='Voir un dashboard')
    dash_get_parser.add_argument('dashboard_id', help='ID du dashboard')

    dash_search_parser = subparsers.add_parser('dashboard-search', help='Rechercher des dashboards')
    dash_search_parser.add_argument('--name', help='Nom du dashboard')
    dash_search_parser.add_argument('--owner', help='Account ID du propriétaire')

    dash_copy_parser = subparsers.add_parser('dashboard-copy', help='Copier un dashboard')
    dash_copy_parser.add_argument('dashboard_id', help='ID du dashboard')
    dash_copy_parser.add_argument('name', help='Nom du nouveau dashboard')
    dash_copy_parser.add_argument('--description', help='Description')

    dash_gadgets_parser = subparsers.add_parser('dashboard-gadgets', help='Voir les gadgets')
    dash_gadgets_parser.add_argument('dashboard_id', help='ID du dashboard')

    # === FILTRES ===

    filter_list_parser = subparsers.add_parser('filter-list', help='Lister les filtres')

    filter_get_parser = subparsers.add_parser('filter-get', help='Voir un filtre')
    filter_get_parser.add_argument('filter_id', type=int, help='ID du filtre')

    filter_search_parser = subparsers.add_parser('filter-search', help='Rechercher des filtres')
    filter_search_parser.add_argument('--name', help='Nom du filtre')
    filter_search_parser.add_argument('--owner', help='Account ID du propriétaire')
    filter_search_parser.add_argument('--favourite', action='store_true', help='Seulement favoris')

    filter_create_parser = subparsers.add_parser('filter-create', help='Créer un filtre')
    filter_create_parser.add_argument('name', help='Nom du filtre')
    filter_create_parser.add_argument('jql', help='Requête JQL')
    filter_create_parser.add_argument('--description', help='Description')
    filter_create_parser.add_argument('--favourite', action='store_true', help='Ajouter aux favoris')

    filter_update_parser = subparsers.add_parser('filter-update', help='Mettre à jour un filtre')
    filter_update_parser.add_argument('filter_id', type=int, help='ID du filtre')
    filter_update_parser.add_argument('--name', help='Nouveau nom')
    filter_update_parser.add_argument('--jql', help='Nouvelle requête JQL')
    filter_update_parser.add_argument('--description', help='Nouvelle description')

    filter_delete_parser = subparsers.add_parser('filter-delete', help='Supprimer un filtre')
    filter_delete_parser.add_argument('filter_id', type=int, help='ID du filtre')
    filter_delete_parser.add_argument('--confirm', action='store_true', help='Confirmer')

    filter_clone_parser = subparsers.add_parser('filter-clone', help='Cloner un filtre')
    filter_clone_parser.add_argument('filter_id', type=int, help='ID du filtre')
    filter_clone_parser.add_argument('new_name', help='Nom du nouveau filtre')

    # Favoris
    fav_list_parser = subparsers.add_parser('favourite-list', help='Lister les filtres favoris')

    fav_add_parser = subparsers.add_parser('favourite-add', help='Ajouter un filtre aux favoris')
    fav_add_parser.add_argument('filter_id', type=int, help='ID du filtre')

    fav_remove_parser = subparsers.add_parser('favourite-remove', help='Retirer un filtre des favoris')
    fav_remove_parser.add_argument('filter_id', type=int, help='ID du filtre')

    # Propriété
    owner_parser = subparsers.add_parser('filter-change-owner', help='Changer le propriétaire d\'un filtre')
    owner_parser.add_argument('filter_id', type=int, help='ID du filtre')
    owner_parser.add_argument('account_id', help='Account ID du nouveau propriétaire')

    # Partage
    share_list_parser = subparsers.add_parser('filter-share-list', help='Permissions de partage')
    share_list_parser.add_argument('filter_id', type=int, help='ID du filtre')

    share_add_parser = subparsers.add_parser('filter-share-add', help='Ajouter une permission')
    share_add_parser.add_argument('filter_id', type=int, help='ID du filtre')
    share_add_parser.add_argument('--type', required=True,
                                  choices=['group', 'project', 'projectRole', 'global', 'authenticated'],
                                  help='Type de permission')
    share_add_parser.add_argument('--project-id', help='ID du projet')
    share_add_parser.add_argument('--group', help='Nom du groupe')
    share_add_parser.add_argument('--role-id', help='ID du rôle')

    # Export
    export_parser = subparsers.add_parser('filter-export', help='Exporter les résultats d\'un filtre')
    export_parser.add_argument('filter_id', type=int, help='ID du filtre')
    export_parser.add_argument('filename', help='Fichier de sortie')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json',
                              help='Format d\'export')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        manager = DashboardFilterManager(client)

        # === DASHBOARDS ===

        if args.command == 'dashboard-list':
            dashboards = manager.list_dashboards(args.max)
            print(f"\n{'ID':<40} {'Nom':<50}")
            print("-" * 90)
            for dash in dashboards:
                print(f"{dash['id']:<40} {dash['name']:<50}")
            print(f"\nTotal: {len(dashboards)} dashboards")

        elif args.command == 'dashboard-get':
            dashboard = manager.get_dashboard(args.dashboard_id)
            if dashboard:
                print(json.dumps(dashboard, indent=2, ensure_ascii=False))
            else:
                print(f"Dashboard {args.dashboard_id} non trouvé", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'dashboard-search':
            dashboards = manager.search_dashboards(args.name, args.owner)
            print(f"\nRésultats de recherche ({len(dashboards)} dashboards):")
            for dash in dashboards:
                print(f"  • [{dash['id']}] {dash['name']}")

        elif args.command == 'dashboard-copy':
            new_dash = manager.copy_dashboard(args.dashboard_id, args.name, args.description)
            if new_dash:
                print(f"✓ Dashboard copié: {new_dash['name']} (ID: {new_dash['id']})")
            else:
                print("✗ Échec de la copie", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'dashboard-gadgets':
            gadgets = manager.get_dashboard_gadgets(args.dashboard_id)
            print(f"\nGadgets du dashboard:")
            for gadget in gadgets:
                print(f"  • {gadget.get('title', 'Sans titre')}")
                print(f"    ID: {gadget.get('id')}")

        # === FILTRES ===

        elif args.command == 'filter-list':
            filters = manager.list_filters()
            print(f"\n{'ID':<10} {'Nom':<50} {'Favori'}")
            print("-" * 65)
            for filt in filters:
                fav = "★" if filt.get('favourite') else "☆"
                print(f"{filt['id']:<10} {filt['name']:<50} {fav}")
            print(f"\nTotal: {len(filters)} filtres")

        elif args.command == 'filter-get':
            filt = manager.get_filter(args.filter_id)
            if filt:
                print(json.dumps(filt, indent=2, ensure_ascii=False))
            else:
                print(f"Filtre {args.filter_id} non trouvé", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'filter-search':
            filters = manager.search_filters(args.name, args.owner, favourite=args.favourite)
            print(f"\nRésultats de recherche ({len(filters)} filtres):")
            for filt in filters:
                fav = "★" if filt.get('favourite') else "☆"
                print(f"  {fav} [{filt['id']}] {filt['name']}")
                print(f"    JQL: {filt.get('jql', 'N/A')}")

        elif args.command == 'filter-create':
            filt = manager.create_filter(args.name, args.jql, args.description, args.favourite)
            if filt:
                print(f"✓ Filtre créé: {filt['name']} (ID: {filt['id']})")
            else:
                print("✗ Échec de la création", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'filter-update':
            filt = manager.update_filter(args.filter_id, args.name, args.jql, args.description)
            if filt:
                print(f"✓ Filtre {args.filter_id} mis à jour")
            else:
                print("✗ Échec de la mise à jour", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'filter-delete':
            if not args.confirm:
                response = input(f"⚠ Confirmer la suppression du filtre {args.filter_id} ? (oui/non): ")
                if response.lower() not in ['oui', 'o', 'yes', 'y']:
                    print("Suppression annulée")
                    return

            if manager.delete_filter(args.filter_id):
                print(f"✓ Filtre {args.filter_id} supprimé")
            else:
                print("✗ Échec de la suppression", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'filter-clone':
            new_filter = manager.clone_filter(args.filter_id, args.new_name)
            if new_filter:
                print(f"✓ Filtre cloné: {new_filter['name']} (ID: {new_filter['id']})")
            else:
                print("✗ Échec du clonage", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'favourite-list':
            filters = manager.get_favourite_filters()
            print(f"\nFiltres favoris ({len(filters)}):")
            for filt in filters:
                print(f"  ★ [{filt['id']}] {filt['name']}")

        elif args.command == 'favourite-add':
            if manager.add_filter_to_favourites(args.filter_id):
                print(f"✓ Filtre {args.filter_id} ajouté aux favoris")
            else:
                print("✗ Échec", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'favourite-remove':
            if manager.remove_filter_from_favourites(args.filter_id):
                print(f"✓ Filtre {args.filter_id} retiré des favoris")
            else:
                print("✗ Échec", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'filter-change-owner':
            if manager.change_filter_owner(args.filter_id, args.account_id):
                print(f"✓ Propriétaire du filtre {args.filter_id} changé")
            else:
                print("✗ Échec du changement", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'filter-share-list':
            permissions = manager.get_filter_share_permissions(args.filter_id)
            print(f"\nPermissions de partage du filtre {args.filter_id}:")
            for perm in permissions:
                print(f"  • Type: {perm.get('type')}")
                if perm.get('project'):
                    print(f"    Projet: {perm['project'].get('name')}")
                if perm.get('group'):
                    print(f"    Groupe: {perm['group'].get('name')}")

        elif args.command == 'filter-share-add':
            result = manager.add_filter_share_permission(
                args.filter_id,
                args.type,
                args.project_id,
                args.group,
                args.role_id
            )
            if result:
                print(f"✓ Permission de partage ajoutée")
            else:
                print("✗ Échec de l'ajout", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'filter-export':
            manager.export_filter_results(args.filter_id, args.filename, args.format)

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
