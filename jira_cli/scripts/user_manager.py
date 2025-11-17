#!/usr/bin/env python3
"""
Script de gestion des utilisateurs Jira Cloud
Permet de lister, rechercher, auditer les utilisateurs
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import List, Dict

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class UserManager:
    """Gestionnaire d'utilisateurs Jira"""

    def __init__(self, client: JiraClient):
        self.client = client

    def list_users(self, max_results: int = 1000) -> List[Dict]:
        """Liste tous les utilisateurs"""
        users = self.client.get_paginated('users/search', max_results=max_results)
        return users

    def search_users(self, query: str) -> List[Dict]:
        """Recherche des utilisateurs par nom ou email"""
        users = self.client.get('user/search', params={'query': query})
        return users if users else []

    def get_user_groups(self, account_id: str) -> List[str]:
        """Récupère les groupes d'un utilisateur"""
        groups = self.client.get_paginated(f'user/groups', params={'accountId': account_id})
        return [g['name'] for g in groups] if groups else []

    def get_inactive_users(self, days: int = 90) -> List[Dict]:
        """
        Identifie les utilisateurs inactifs
        Note: Nécessite l'API d'audit pour une vraie détection d'inactivité
        """
        all_users = self.list_users()
        inactive = []

        for user in all_users:
            if not user.get('active', True):
                inactive.append({
                    'accountId': user.get('accountId'),
                    'displayName': user.get('displayName'),
                    'emailAddress': user.get('emailAddress'),
                    'active': user.get('active')
                })

        return inactive

    def export_users_csv(self, filename: str):
        """Exporte la liste des utilisateurs en CSV"""
        import csv

        users = self.list_users()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if not users:
                print("Aucun utilisateur trouvé")
                return

            writer = csv.DictWriter(f, fieldnames=[
                'accountId', 'displayName', 'emailAddress', 'active', 'accountType'
            ])
            writer.writeheader()

            for user in users:
                writer.writerow({
                    'accountId': user.get('accountId', ''),
                    'displayName': user.get('displayName', ''),
                    'emailAddress': user.get('emailAddress', 'N/A'),
                    'active': user.get('active', True),
                    'accountType': user.get('accountType', 'atlassian')
                })

        print(f"✓ {len(users)} utilisateurs exportés vers {filename}")

    def get_user_permissions_summary(self, account_id: str) -> Dict:
        """Résumé des permissions d'un utilisateur"""
        user = self.client.get('user', params={'accountId': account_id})
        groups = self.get_user_groups(account_id)

        return {
            'user': user,
            'groups': groups,
            'group_count': len(groups)
        }

    def audit_user_access(self) -> Dict:
        """Audit complet des accès utilisateurs"""
        all_users = self.list_users()
        inactive_users = self.get_inactive_users()

        active_count = sum(1 for u in all_users if u.get('active', True))
        inactive_count = len(all_users) - active_count

        return {
            'total_users': len(all_users),
            'active_users': active_count,
            'inactive_users': inactive_count,
            'inactive_list': inactive_users,
            'audit_date': datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser(description='Gestion des utilisateurs Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Liste des utilisateurs
    list_parser = subparsers.add_parser('list', help='Lister tous les utilisateurs')
    list_parser.add_argument('--format', choices=['json', 'table'], default='table',
                            help='Format de sortie')
    list_parser.add_argument('--max', type=int, default=1000,
                            help='Nombre maximum d\'utilisateurs')

    # Recherche d'utilisateurs
    search_parser = subparsers.add_parser('search', help='Rechercher un utilisateur')
    search_parser.add_argument('query', help='Terme de recherche')

    # Groupes d'un utilisateur
    groups_parser = subparsers.add_parser('groups', help='Groupes d\'un utilisateur')
    groups_parser.add_argument('account_id', help='Account ID de l\'utilisateur')

    # Utilisateurs inactifs
    inactive_parser = subparsers.add_parser('inactive', help='Utilisateurs inactifs')
    inactive_parser.add_argument('--days', type=int, default=90,
                                help='Nombre de jours d\'inactivité')

    # Export CSV
    export_parser = subparsers.add_parser('export', help='Exporter les utilisateurs en CSV')
    export_parser.add_argument('filename', help='Nom du fichier CSV')

    # Audit
    audit_parser = subparsers.add_parser('audit', help='Audit des accès utilisateurs')
    audit_parser.add_argument('--output', help='Fichier de sortie JSON')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        manager = UserManager(client)

        if args.command == 'list':
            users = manager.list_users(max_results=args.max)

            if args.format == 'json':
                print(json.dumps(users, indent=2, ensure_ascii=False))
            else:
                print(f"\n{'Account ID':<40} {'Nom':<30} {'Email':<40} {'Actif'}")
                print("-" * 120)
                for user in users:
                    print(f"{user.get('accountId', 'N/A'):<40} "
                          f"{user.get('displayName', 'N/A'):<30} "
                          f"{user.get('emailAddress', 'N/A'):<40} "
                          f"{'✓' if user.get('active', True) else '✗'}")
                print(f"\nTotal: {len(users)} utilisateurs")

        elif args.command == 'search':
            users = manager.search_users(args.query)
            print(json.dumps(users, indent=2, ensure_ascii=False))

        elif args.command == 'groups':
            groups = manager.get_user_groups(args.account_id)
            print(f"\nGroupes de l'utilisateur {args.account_id}:")
            for group in groups:
                print(f"  • {group}")
            print(f"\nTotal: {len(groups)} groupes")

        elif args.command == 'inactive':
            inactive = manager.get_inactive_users(args.days)
            print(f"\nUtilisateurs inactifs:")
            for user in inactive:
                print(f"  • {user['displayName']} ({user.get('emailAddress', 'N/A')})")
            print(f"\nTotal: {len(inactive)} utilisateurs inactifs")

        elif args.command == 'export':
            manager.export_users_csv(args.filename)

        elif args.command == 'audit':
            audit = manager.audit_user_access()

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(audit, f, indent=2, ensure_ascii=False)
                print(f"✓ Audit exporté vers {args.output}")
            else:
                print("\n=== AUDIT DES ACCÈS UTILISATEURS ===")
                print(f"Date: {audit['audit_date']}")
                print(f"Total utilisateurs: {audit['total_users']}")
                print(f"Actifs: {audit['active_users']}")
                print(f"Inactifs: {audit['inactive_users']}")

                if audit['inactive_list']:
                    print("\nUtilisateurs inactifs:")
                    for user in audit['inactive_list']:
                        print(f"  • {user['displayName']}")

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
