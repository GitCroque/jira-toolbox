#!/usr/bin/env python3
"""
Script d'opérations en masse sur Jira Cloud
Permet de créer, modifier, supprimer, transitionner des issues en masse
Import/export CSV, traitement par lots
"""

import sys
import os
import argparse
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class BulkOperations:
    """Gestionnaire d'opérations en masse"""

    def __init__(self, client: JiraClient):
        self.client = client
        self.batch_size = 50  # Taille des lots pour éviter les timeouts
        self.delay_between_batches = 1  # Secondes entre les lots

    def bulk_create_issues(self, issues_data: List[Dict], dry_run: bool = False) -> Dict:
        """
        Crée plusieurs issues en masse

        Args:
            issues_data: Liste de données d'issues
            dry_run: Mode simulation (ne crée rien)

        Returns:
            Résultat avec succès et échecs
        """
        results = {
            'created': [],
            'failed': [],
            'total': len(issues_data),
            'dry_run': dry_run
        }

        if dry_run:
            print(f"MODE SIMULATION: {len(issues_data)} issues seraient créées")
            for i, issue_data in enumerate(issues_data, 1):
                print(f"  {i}. {issue_data.get('fields', {}).get('summary', 'N/A')}")
            return results

        # Traiter par lots
        for i in range(0, len(issues_data), self.batch_size):
            batch = issues_data[i:i + self.batch_size]
            print(f"Traitement du lot {i//self.batch_size + 1}/{(len(issues_data)-1)//self.batch_size + 1}...")

            for issue_data in batch:
                try:
                    result = self.client.post('issue', data=issue_data)
                    if result:
                        results['created'].append({
                            'key': result.get('key'),
                            'summary': issue_data.get('fields', {}).get('summary')
                        })
                        print(f"  ✓ {result.get('key')}")
                    else:
                        results['failed'].append({
                            'data': issue_data,
                            'error': 'API returned None'
                        })
                        print(f"  ✗ Échec: {issue_data.get('fields', {}).get('summary')}")
                except Exception as e:
                    results['failed'].append({
                        'data': issue_data,
                        'error': str(e)
                    })
                    print(f"  ✗ Erreur: {str(e)}")

            # Pause entre les lots
            if i + self.batch_size < len(issues_data):
                time.sleep(self.delay_between_batches)

        return results

    def bulk_update_issues(self, updates: List[Dict], dry_run: bool = False) -> Dict:
        """
        Met à jour plusieurs issues en masse

        Args:
            updates: Liste de {issue_key, fields}
            dry_run: Mode simulation
        """
        results = {
            'updated': [],
            'failed': [],
            'total': len(updates),
            'dry_run': dry_run
        }

        if dry_run:
            print(f"MODE SIMULATION: {len(updates)} issues seraient mises à jour")
            for update in updates:
                print(f"  • {update['issue_key']}: {list(update.get('fields', {}).keys())}")
            return results

        for i in range(0, len(updates), self.batch_size):
            batch = updates[i:i + self.batch_size]
            print(f"Traitement du lot {i//self.batch_size + 1}...")

            for update in batch:
                try:
                    issue_key = update['issue_key']
                    fields = update.get('fields', {})

                    update_data = {'fields': fields}
                    result = self.client.put(f'issue/{issue_key}', data=update_data)

                    if result is not None:
                        results['updated'].append(issue_key)
                        print(f"  ✓ {issue_key}")
                    else:
                        results['failed'].append({
                            'issue_key': issue_key,
                            'error': 'Update failed'
                        })
                        print(f"  ✗ {issue_key}")

                except Exception as e:
                    results['failed'].append({
                        'issue_key': update.get('issue_key'),
                        'error': str(e)
                    })
                    print(f"  ✗ Erreur: {str(e)}")

            if i + self.batch_size < len(updates):
                time.sleep(self.delay_between_batches)

        return results

    def bulk_delete_issues(self, issue_keys: List[str], dry_run: bool = False,
                          delete_subtasks: bool = False) -> Dict:
        """Supprime plusieurs issues en masse"""
        results = {
            'deleted': [],
            'failed': [],
            'total': len(issue_keys),
            'dry_run': dry_run
        }

        if dry_run:
            print(f"MODE SIMULATION: {len(issue_keys)} issues seraient supprimées")
            for key in issue_keys:
                print(f"  • {key}")
            return results

        for i in range(0, len(issue_keys), self.batch_size):
            batch = issue_keys[i:i + self.batch_size]
            print(f"Traitement du lot {i//self.batch_size + 1}...")

            for issue_key in batch:
                try:
                    import requests
                    url = f"{self.client.base_url}/rest/api/3/issue/{issue_key}"
                    params = {'deleteSubtasks': 'true' if delete_subtasks else 'false'}

                    response = requests.delete(url, auth=self.client.auth, params=params)

                    if response.status_code in [204, 200]:
                        results['deleted'].append(issue_key)
                        print(f"  ✓ {issue_key}")
                    else:
                        results['failed'].append({
                            'issue_key': issue_key,
                            'error': f'HTTP {response.status_code}'
                        })
                        print(f"  ✗ {issue_key} (HTTP {response.status_code})")

                except Exception as e:
                    results['failed'].append({
                        'issue_key': issue_key,
                        'error': str(e)
                    })
                    print(f"  ✗ Erreur: {str(e)}")

            if i + self.batch_size < len(issue_keys):
                time.sleep(self.delay_between_batches)

        return results

    def bulk_transition_issues(self, issue_keys: List[str], transition_name: str,
                              comment: str = None, dry_run: bool = False) -> Dict:
        """Effectue une transition sur plusieurs issues"""
        results = {
            'transitioned': [],
            'failed': [],
            'total': len(issue_keys),
            'dry_run': dry_run
        }

        if dry_run:
            print(f"MODE SIMULATION: {len(issue_keys)} issues → {transition_name}")
            for key in issue_keys:
                print(f"  • {key}")
            return results

        for i in range(0, len(issue_keys), self.batch_size):
            batch = issue_keys[i:i + self.batch_size]
            print(f"Traitement du lot {i//self.batch_size + 1}...")

            for issue_key in batch:
                try:
                    # Récupérer les transitions disponibles
                    transitions = self.client.get(f'issue/{issue_key}/transitions')

                    if not transitions:
                        results['failed'].append({
                            'issue_key': issue_key,
                            'error': 'Cannot get transitions'
                        })
                        continue

                    # Trouver l'ID de la transition
                    transition_id = None
                    for t in transitions.get('transitions', []):
                        if t['name'].lower() == transition_name.lower():
                            transition_id = t['id']
                            break

                    if not transition_id:
                        results['failed'].append({
                            'issue_key': issue_key,
                            'error': f'Transition "{transition_name}" not found'
                        })
                        print(f"  ✗ {issue_key} (transition non trouvée)")
                        continue

                    # Effectuer la transition
                    transition_data = {'transition': {'id': transition_id}}

                    if comment:
                        transition_data['update'] = {
                            'comment': [{
                                'add': {
                                    'body': {
                                        'type': 'doc',
                                        'version': 1,
                                        'content': [{
                                            'type': 'paragraph',
                                            'content': [{'type': 'text', 'text': comment}]
                                        }]
                                    }
                                }
                            }]
                        }

                    result = self.client.post(f'issue/{issue_key}/transitions',
                                             data=transition_data)

                    if result is not None:
                        results['transitioned'].append(issue_key)
                        print(f"  ✓ {issue_key}")
                    else:
                        results['failed'].append({
                            'issue_key': issue_key,
                            'error': 'Transition failed'
                        })
                        print(f"  ✗ {issue_key}")

                except Exception as e:
                    results['failed'].append({
                        'issue_key': issue_key,
                        'error': str(e)
                    })
                    print(f"  ✗ Erreur {issue_key}: {str(e)}")

            if i + self.batch_size < len(issue_keys):
                time.sleep(self.delay_between_batches)

        return results

    def import_from_csv(self, csv_file: str, project_key: str,
                       issue_type: str = 'Task', dry_run: bool = False) -> Dict:
        """
        Importe des issues depuis un fichier CSV

        Format CSV attendu: summary,description,priority,assignee,labels
        """
        issues_data = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                issue_data = {
                    'fields': {
                        'project': {'key': project_key},
                        'summary': row.get('summary', ''),
                        'issuetype': {'name': issue_type}
                    }
                }

                # Description
                if row.get('description'):
                    issue_data['fields']['description'] = {
                        'type': 'doc',
                        'version': 1,
                        'content': [{
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': row['description']}]
                        }]
                    }

                # Priorité
                if row.get('priority'):
                    issue_data['fields']['priority'] = {'name': row['priority']}

                # Assigné
                if row.get('assignee'):
                    issue_data['fields']['assignee'] = {'id': row['assignee']}

                # Labels
                if row.get('labels'):
                    labels = [l.strip() for l in row['labels'].split(',')]
                    issue_data['fields']['labels'] = labels

                issues_data.append(issue_data)

        print(f"Importation de {len(issues_data)} issues depuis {csv_file}")
        return self.bulk_create_issues(issues_data, dry_run=dry_run)

    def export_to_csv(self, jql: str, csv_file: str,
                     fields: List[str] = None) -> int:
        """
        Exporte les résultats d'une recherche JQL en CSV

        Args:
            jql: Requête JQL
            csv_file: Fichier de sortie
            fields: Champs à exporter (par défaut: summary, status, assignee, priority)
        """
        if not fields:
            fields = ['summary', 'status', 'assignee', 'priority', 'created', 'updated']

        # Rechercher les issues
        params = {
            'jql': jql,
            'fields': ','.join(fields)
        }

        issues = self.client.get_paginated('search', params=params)

        # Écrire le CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            # Préparer les en-têtes
            csv_fields = ['key'] + fields

            writer = csv.DictWriter(f, fieldnames=csv_fields)
            writer.writeheader()

            for issue in issues:
                row = {'key': issue['key']}
                issue_fields = issue.get('fields', {})

                for field in fields:
                    value = issue_fields.get(field)

                    # Traiter les différents types de champs
                    if isinstance(value, dict):
                        if 'name' in value:
                            row[field] = value['name']
                        elif 'displayName' in value:
                            row[field] = value['displayName']
                        else:
                            row[field] = str(value)
                    elif isinstance(value, list):
                        row[field] = ', '.join(str(v) for v in value)
                    else:
                        row[field] = value or ''

                writer.writerow(row)

        print(f"✓ {len(issues)} issues exportées vers {csv_file}")
        return len(issues)

    def bulk_assign_issues(self, issue_keys: List[str], account_id: str = None,
                          dry_run: bool = False) -> Dict:
        """Assigne plusieurs issues en masse"""
        results = {
            'assigned': [],
            'failed': [],
            'total': len(issue_keys),
            'dry_run': dry_run
        }

        assignee_name = account_id or "Automatic"

        if dry_run:
            print(f"MODE SIMULATION: {len(issue_keys)} issues → {assignee_name}")
            for key in issue_keys:
                print(f"  • {key}")
            return results

        for i in range(0, len(issue_keys), self.batch_size):
            batch = issue_keys[i:i + self.batch_size]
            print(f"Traitement du lot {i//self.batch_size + 1}...")

            for issue_key in batch:
                try:
                    data = {'accountId': account_id} if account_id else None
                    result = self.client.put(f'issue/{issue_key}/assignee', data=data)

                    if result is not None:
                        results['assigned'].append(issue_key)
                        print(f"  ✓ {issue_key}")
                    else:
                        results['failed'].append({
                            'issue_key': issue_key,
                            'error': 'Assignment failed'
                        })
                        print(f"  ✗ {issue_key}")

                except Exception as e:
                    results['failed'].append({
                        'issue_key': issue_key,
                        'error': str(e)
                    })
                    print(f"  ✗ Erreur: {str(e)}")

            if i + self.batch_size < len(issue_keys):
                time.sleep(self.delay_between_batches)

        return results


def main():
    parser = argparse.ArgumentParser(description='Opérations en masse sur Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')
    parser.add_argument('--dry-run', action='store_true',
                       help='Mode simulation (ne fait rien)')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Création en masse
    create_parser = subparsers.add_parser('create', help='Créer des issues en masse')
    create_parser.add_argument('json_file', help='Fichier JSON avec les issues')

    # Mise à jour en masse
    update_parser = subparsers.add_parser('update', help='Mettre à jour des issues en masse')
    update_parser.add_argument('json_file', help='Fichier JSON avec les mises à jour')

    # Suppression en masse
    delete_parser = subparsers.add_parser('delete', help='Supprimer des issues en masse')
    delete_parser.add_argument('--jql', help='JQL pour sélectionner les issues')
    delete_parser.add_argument('--keys', nargs='+', help='Clés des issues')
    delete_parser.add_argument('--delete-subtasks', action='store_true',
                              help='Supprimer aussi les sous-tâches')
    delete_parser.add_argument('--confirm', action='store_true',
                              help='Confirmer la suppression')

    # Transition en masse
    transition_parser = subparsers.add_parser('transition',
                                             help='Transitionner des issues en masse')
    transition_parser.add_argument('transition', help='Nom de la transition')
    transition_parser.add_argument('--jql', help='JQL pour sélectionner les issues')
    transition_parser.add_argument('--keys', nargs='+', help='Clés des issues')
    transition_parser.add_argument('--comment', help='Commentaire')

    # Import CSV
    import_parser = subparsers.add_parser('import-csv', help='Importer depuis un CSV')
    import_parser.add_argument('csv_file', help='Fichier CSV')
    import_parser.add_argument('project_key', help='Clé du projet')
    import_parser.add_argument('--type', default='Task', help='Type d\'issue')

    # Export CSV
    export_parser = subparsers.add_parser('export-csv', help='Exporter vers un CSV')
    export_parser.add_argument('jql', help='Requête JQL')
    export_parser.add_argument('csv_file', help='Fichier CSV de sortie')
    export_parser.add_argument('--fields', nargs='*', help='Champs à exporter')

    # Assignation en masse
    assign_parser = subparsers.add_parser('assign', help='Assigner des issues en masse')
    assign_parser.add_argument('--jql', help='JQL pour sélectionner les issues')
    assign_parser.add_argument('--keys', nargs='+', help='Clés des issues')
    assign_parser.add_argument('--account-id', help='Account ID (vide = automatic)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        bulk = BulkOperations(client)

        if args.command == 'create':
            with open(args.json_file, 'r') as f:
                issues_data = json.load(f)

            results = bulk.bulk_create_issues(issues_data, dry_run=args.dry_run)

            print(f"\n=== RÉSULTATS ===")
            print(f"Total: {results['total']}")
            print(f"Créées: {len(results['created'])}")
            print(f"Échecs: {len(results['failed'])}")

            if results['failed']:
                print(f"\nÉchecs:")
                for fail in results['failed'][:10]:  # 10 premiers
                    print(f"  • {fail.get('error')}")

        elif args.command == 'update':
            with open(args.json_file, 'r') as f:
                updates = json.load(f)

            results = bulk.bulk_update_issues(updates, dry_run=args.dry_run)

            print(f"\n=== RÉSULTATS ===")
            print(f"Total: {results['total']}")
            print(f"Mises à jour: {len(results['updated'])}")
            print(f"Échecs: {len(results['failed'])}")

        elif args.command == 'delete':
            # Récupérer les clés à supprimer
            if args.jql:
                issues = client.get_paginated('search', params={'jql': args.jql, 'fields': 'key'})
                issue_keys = [i['key'] for i in issues]
            elif args.keys:
                issue_keys = args.keys
            else:
                print("Erreur: spécifier --jql ou --keys", file=sys.stderr)
                sys.exit(1)

            if not args.confirm and not args.dry_run:
                response = input(f"⚠ Confirmer la suppression de {len(issue_keys)} issues ? (oui/non): ")
                if response.lower() not in ['oui', 'o', 'yes', 'y']:
                    print("Suppression annulée")
                    return

            results = bulk.bulk_delete_issues(issue_keys, dry_run=args.dry_run,
                                             delete_subtasks=args.delete_subtasks)

            print(f"\n=== RÉSULTATS ===")
            print(f"Total: {results['total']}")
            print(f"Supprimées: {len(results['deleted'])}")
            print(f"Échecs: {len(results['failed'])}")

        elif args.command == 'transition':
            # Récupérer les clés
            if args.jql:
                issues = client.get_paginated('search', params={'jql': args.jql, 'fields': 'key'})
                issue_keys = [i['key'] for i in issues]
            elif args.keys:
                issue_keys = args.keys
            else:
                print("Erreur: spécifier --jql ou --keys", file=sys.stderr)
                sys.exit(1)

            results = bulk.bulk_transition_issues(issue_keys, args.transition,
                                                 args.comment, dry_run=args.dry_run)

            print(f"\n=== RÉSULTATS ===")
            print(f"Total: {results['total']}")
            print(f"Transitionnées: {len(results['transitioned'])}")
            print(f"Échecs: {len(results['failed'])}")

        elif args.command == 'import-csv':
            results = bulk.import_from_csv(args.csv_file, args.project_key,
                                          args.type, dry_run=args.dry_run)

            print(f"\n=== RÉSULTATS ===")
            print(f"Total: {results['total']}")
            print(f"Créées: {len(results['created'])}")
            print(f"Échecs: {len(results['failed'])}")

        elif args.command == 'export-csv':
            count = bulk.export_to_csv(args.jql, args.csv_file, args.fields)

        elif args.command == 'assign':
            # Récupérer les clés
            if args.jql:
                issues = client.get_paginated('search', params={'jql': args.jql, 'fields': 'key'})
                issue_keys = [i['key'] for i in issues]
            elif args.keys:
                issue_keys = args.keys
            else:
                print("Erreur: spécifier --jql ou --keys", file=sys.stderr)
                sys.exit(1)

            results = bulk.bulk_assign_issues(issue_keys, args.account_id,
                                             dry_run=args.dry_run)

            print(f"\n=== RÉSULTATS ===")
            print(f"Total: {results['total']}")
            print(f"Assignées: {len(results['assigned'])}")
            print(f"Échecs: {len(results['failed'])}")

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
