#!/usr/bin/env python3
"""
Script de gestion des utilisateurs Jira Cloud
Permet de lister, rechercher, auditer et nettoyer les utilisateurs
"""

import sys
import os
import argparse
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

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

    def list_active_users(self, max_results: int = 1000) -> List[Dict]:
        """Liste uniquement les utilisateurs actifs"""
        all_users = self.list_users(max_results=max_results)
        return [u for u in all_users if u.get('active', True)]

    def list_disabled_users(self, max_results: int = 1000) -> List[Dict]:
        """Liste uniquement les utilisateurs désactivés"""
        all_users = self.list_users(max_results=max_results)
        return [u for u in all_users if not u.get('active', True)]

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

    def get_users_by_last_login(self, days_back: int = 90, max_results: int = 1000) -> List[Dict]:
        """
        Liste les utilisateurs avec leur dernière date de connexion
        Utilise l'API d'audit pour récupérer les dernières connexions
        """
        all_users = self.list_users(max_results=max_results)
        users_with_login = []

        # Date de début pour la recherche d'audit
        from_date = datetime.now() - timedelta(days=days_back)
        from_str = from_date.strftime('%Y-%m-%d')

        print(f"Récupération des logs d'audit depuis {from_str}...", file=sys.stderr)

        # Récupérer les logs d'audit pour les connexions
        try:
            # L'API d'audit nécessite des permissions spécifiques
            audit_records = self.client.get_paginated(
                'auditing/record',
                params={
                    'filter': 'User logged in',
                    'from': from_str,
                    'to': datetime.now().strftime('%Y-%m-%d')
                },
                max_results=1000
            )

            # Créer un dictionnaire des dernières connexions par accountId
            last_logins = {}
            for record in audit_records:
                account_id = record.get('authorAccountId')
                created = record.get('created')
                if account_id and created:
                    if account_id not in last_logins or created > last_logins[account_id]:
                        last_logins[account_id] = created

            # Enrichir les utilisateurs avec leur dernière connexion
            for user in all_users:
                account_id = user.get('accountId')
                user_data = user.copy()
                user_data['lastLogin'] = last_logins.get(account_id, 'Aucune connexion récente')
                users_with_login.append(user_data)

            # Trier par dernière connexion (les plus récents d'abord)
            users_with_login.sort(
                key=lambda u: u.get('lastLogin', '0000-00-00'),
                reverse=True
            )

        except Exception as e:
            print(f"⚠ Impossible de récupérer les logs d'audit: {e}", file=sys.stderr)
            print(f"⚠ Vérifiez que vous avez les permissions d'accès à l'API d'audit", file=sys.stderr)
            # Retourner quand même les utilisateurs sans info de connexion
            users_with_login = all_users

        return users_with_login

    def delete_user(self, account_id: str) -> bool:
        """
        Supprime un utilisateur
        Note: L'API Jira Cloud ne permet pas de supprimer directement les utilisateurs
        mais de les désactiver via l'interface admin
        """
        try:
            # Vérifier si l'utilisateur existe
            user = self.client.get('user', params={'accountId': account_id})

            print(f"⚠ L'API Jira Cloud ne permet pas de supprimer directement les utilisateurs.", file=sys.stderr)
            print(f"⚠ Vous devez désactiver l'utilisateur via l'interface admin:", file=sys.stderr)
            print(f"   https://{self.client.base_url.split('//')[1]}/admin/users", file=sys.stderr)
            print(f"\nUtilisateur à désactiver:", file=sys.stderr)
            print(f"  • Nom: {user.get('displayName')}", file=sys.stderr)
            print(f"  • Email: {user.get('emailAddress')}", file=sys.stderr)
            print(f"  • Account ID: {account_id}", file=sys.stderr)

            return False

        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur: {e}", file=sys.stderr)
            return False

    def delete_disabled_users(self, dry_run: bool = True, confirm: bool = False) -> Dict:
        """
        Supprime tous les utilisateurs désactivés

        Args:
            dry_run: Si True, simule uniquement l'opération
            confirm: Si True, procède sans demander de confirmation

        Returns:
            Dictionnaire avec les résultats
        """
        disabled_users = self.list_disabled_users()

        if not disabled_users:
            print("✓ Aucun utilisateur désactivé trouvé")
            return {'deleted': 0, 'failed': 0, 'users': []}

        print(f"\n{'='*60}")
        print(f"NETTOYAGE DES UTILISATEURS DÉSACTIVÉS")
        print(f"{'='*60}\n")
        print(f"Nombre d'utilisateurs désactivés trouvés: {len(disabled_users)}\n")

        # Afficher la liste
        for i, user in enumerate(disabled_users[:10], 1):
            print(f"  {i}. {user.get('displayName')} ({user.get('emailAddress', 'N/A')})")

        if len(disabled_users) > 10:
            print(f"  ... et {len(disabled_users) - 10} autres\n")

        if dry_run:
            print("\n⚠ MODE SIMULATION (dry-run) - Aucune suppression ne sera effectuée")
            print("⚠ Pour effectuer les suppressions, utilisez --no-dry-run\n")
            return {
                'dry_run': True,
                'would_delete': len(disabled_users),
                'users': disabled_users
            }

        # Information importante
        print("\n" + "!"*60)
        print("⚠ IMPORTANT: L'API Jira Cloud ne permet pas de supprimer")
        print("   directement les utilisateurs via l'API REST.")
        print("\n📋 OPTIONS DISPONIBLES:")
        print("   1. Désactivation manuelle via l'admin Jira")
        print("   2. Utilisation de l'API Admin Jira (requiert des droits spéciaux)")
        print("   3. Export de la liste pour traitement par votre équipe IT")
        print("!"*60 + "\n")

        # Proposer d'exporter la liste
        export_file = f"disabled_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        print(f"💾 Export de la liste vers: {export_file}")

        self.export_users_to_csv(disabled_users, export_file)

        return {
            'dry_run': False,
            'exported_to': export_file,
            'count': len(disabled_users),
            'users': disabled_users,
            'message': 'Liste exportée - suppression manuelle requise'
        }

    def export_users_to_csv(self, users: List[Dict], filename: str):
        """Exporte une liste d'utilisateurs spécifique en CSV"""
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if not users:
                print("Aucun utilisateur à exporter")
                return

            writer = csv.DictWriter(f, fieldnames=[
                'accountId', 'displayName', 'emailAddress', 'active',
                'accountType', 'lastLogin'
            ])
            writer.writeheader()

            for user in users:
                writer.writerow({
                    'accountId': user.get('accountId', ''),
                    'displayName': user.get('displayName', ''),
                    'emailAddress': user.get('emailAddress', 'N/A'),
                    'active': user.get('active', True),
                    'accountType': user.get('accountType', 'atlassian'),
                    'lastLogin': user.get('lastLogin', 'N/A')
                })

        print(f"✓ {len(users)} utilisateurs exportés vers {filename}")

    def cleanup_users_interactive(self) -> Dict:
        """
        Nettoyage interactif des utilisateurs avec plusieurs options
        """
        print("\n" + "="*60)
        print("NETTOYAGE INTERACTIF DES UTILISATEURS")
        print("="*60 + "\n")

        all_users = self.list_users()
        disabled_users = self.list_disabled_users()
        active_users = self.list_active_users()

        print(f"📊 STATISTIQUES:")
        print(f"   Total utilisateurs: {len(all_users)}")
        print(f"   Actifs: {len(active_users)}")
        print(f"   Désactivés: {len(disabled_users)}\n")

        # Analyser les utilisateurs par type de compte
        by_type = defaultdict(int)
        for user in all_users:
            by_type[user.get('accountType', 'atlassian')] += 1

        print(f"📊 PAR TYPE DE COMPTE:")
        for acc_type, count in by_type.items():
            print(f"   {acc_type}: {count}")

        print("\n" + "="*60)

        result = {
            'total_users': len(all_users),
            'active_users': len(active_users),
            'disabled_users': len(disabled_users),
            'by_type': dict(by_type)
        }

        return result


def main():
    parser = argparse.ArgumentParser(description='Gestion et nettoyage des utilisateurs Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Liste des utilisateurs
    list_parser = subparsers.add_parser('list', help='Lister tous les utilisateurs')
    list_parser.add_argument('--format', choices=['json', 'table'], default='table',
                            help='Format de sortie')
    list_parser.add_argument('--max', type=int, default=1000,
                            help='Nombre maximum d\'utilisateurs')

    # Liste des utilisateurs actifs
    list_active_parser = subparsers.add_parser('list-active', help='Lister uniquement les utilisateurs actifs')
    list_active_parser.add_argument('--format', choices=['json', 'table'], default='table',
                                   help='Format de sortie')
    list_active_parser.add_argument('--max', type=int, default=1000,
                                   help='Nombre maximum d\'utilisateurs')

    # Liste des utilisateurs désactivés
    list_disabled_parser = subparsers.add_parser('list-disabled', help='Lister uniquement les utilisateurs désactivés')
    list_disabled_parser.add_argument('--format', choices=['json', 'table'], default='table',
                                     help='Format de sortie')
    list_disabled_parser.add_argument('--max', type=int, default=1000,
                                     help='Nombre maximum d\'utilisateurs')

    # Liste par dernière connexion
    list_by_login_parser = subparsers.add_parser('list-by-login',
                                                 help='Lister les utilisateurs par dernière connexion')
    list_by_login_parser.add_argument('--days', type=int, default=90,
                                     help='Nombre de jours à analyser')
    list_by_login_parser.add_argument('--format', choices=['json', 'table', 'csv'], default='table',
                                     help='Format de sortie')
    list_by_login_parser.add_argument('--output', help='Fichier de sortie (pour CSV)')

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

    # Supprimer un utilisateur
    delete_user_parser = subparsers.add_parser('delete-user',
                                              help='Informations pour supprimer un utilisateur')
    delete_user_parser.add_argument('account_id', help='Account ID de l\'utilisateur')

    # Supprimer tous les utilisateurs désactivés
    delete_disabled_parser = subparsers.add_parser('delete-disabled',
                                                   help='Supprimer tous les utilisateurs désactivés')
    delete_disabled_parser.add_argument('--no-dry-run', action='store_true',
                                       help='Effectuer réellement les suppressions (par défaut: simulation)')
    delete_disabled_parser.add_argument('--confirm', action='store_true',
                                       help='Ne pas demander de confirmation')

    # Nettoyage interactif
    cleanup_parser = subparsers.add_parser('cleanup',
                                          help='Nettoyage interactif des utilisateurs')

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

        elif args.command == 'list-active':
            users = manager.list_active_users(max_results=args.max)

            if args.format == 'json':
                print(json.dumps(users, indent=2, ensure_ascii=False))
            else:
                print(f"\n{'Account ID':<40} {'Nom':<30} {'Email':<40}")
                print("-" * 110)
                for user in users:
                    print(f"{user.get('accountId', 'N/A'):<40} "
                          f"{user.get('displayName', 'N/A'):<30} "
                          f"{user.get('emailAddress', 'N/A'):<40}")
                print(f"\n✓ Total: {len(users)} utilisateurs actifs")

        elif args.command == 'list-disabled':
            users = manager.list_disabled_users(max_results=args.max)

            if args.format == 'json':
                print(json.dumps(users, indent=2, ensure_ascii=False))
            else:
                print(f"\n{'Account ID':<40} {'Nom':<30} {'Email':<40}")
                print("-" * 110)
                for user in users:
                    print(f"{user.get('accountId', 'N/A'):<40} "
                          f"{user.get('displayName', 'N/A'):<30} "
                          f"{user.get('emailAddress', 'N/A'):<40}")
                print(f"\n✗ Total: {len(users)} utilisateurs désactivés")

        elif args.command == 'list-by-login':
            users = manager.get_users_by_last_login(days_back=args.days)

            if args.format == 'json':
                print(json.dumps(users, indent=2, ensure_ascii=False))
            elif args.format == 'csv':
                output_file = args.output or f'users_by_login_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                manager.export_users_to_csv(users, output_file)
            else:
                print(f"\n{'Nom':<30} {'Email':<40} {'Dernière connexion':<25} {'Actif'}")
                print("-" * 125)
                for user in users:
                    last_login = user.get('lastLogin', 'N/A')
                    # Formatter la date si c'est une vraie date
                    if last_login != 'N/A' and last_login != 'Aucune connexion récente':
                        try:
                            dt = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
                            last_login = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            pass

                    print(f"{user.get('displayName', 'N/A'):<30} "
                          f"{user.get('emailAddress', 'N/A'):<40} "
                          f"{last_login:<25} "
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

        elif args.command == 'delete-user':
            manager.delete_user(args.account_id)

        elif args.command == 'delete-disabled':
            result = manager.delete_disabled_users(
                dry_run=not args.no_dry_run,
                confirm=args.confirm
            )

            if result.get('dry_run'):
                print(f"\n📊 RÉSUMÉ (simulation):")
                print(f"   Utilisateurs qui seraient supprimés: {result.get('would_delete', 0)}")
            else:
                print(f"\n✓ Opération terminée")
                print(f"   {result.get('message', '')}")

        elif args.command == 'cleanup':
            result = manager.cleanup_users_interactive()
            print(f"\n✓ Analyse terminée")

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
