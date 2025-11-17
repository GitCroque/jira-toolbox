#!/usr/bin/env python3
"""
Script de gestion des issues (work items) Jira Cloud
Permet de créer, éditer, supprimer, commenter, gérer les transitions, etc.
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class IssueManager:
    """Gestionnaire d'issues Jira"""

    def __init__(self, client: JiraClient):
        self.client = client

    def create_issue(self, project_key: str, summary: str, issue_type: str,
                     description: str = None, priority: str = None,
                     assignee: str = None, labels: List[str] = None,
                     components: List[str] = None, **custom_fields) -> Dict:
        """Crée une nouvelle issue"""
        fields = {
            'project': {'key': project_key},
            'summary': summary,
            'issuetype': {'name': issue_type}
        }

        if description:
            fields['description'] = {
                'type': 'doc',
                'version': 1,
                'content': [{
                    'type': 'paragraph',
                    'content': [{'type': 'text', 'text': description}]
                }]
            }

        if priority:
            fields['priority'] = {'name': priority}

        if assignee:
            fields['assignee'] = {'id': assignee}

        if labels:
            fields['labels'] = labels

        if components:
            fields['components'] = [{'name': c} for c in components]

        # Ajouter les custom fields
        fields.update(custom_fields)

        issue_data = {'fields': fields}
        return self.client.post('issue', data=issue_data)

    def get_issue(self, issue_key: str, fields: List[str] = None) -> Dict:
        """Récupère les détails d'une issue"""
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
        return self.client.get(f'issue/{issue_key}', params=params)

    def update_issue(self, issue_key: str, **fields) -> bool:
        """Met à jour une issue"""
        update_data = {'fields': fields}
        result = self.client.put(f'issue/{issue_key}', data=update_data)
        return result is not None

    def delete_issue(self, issue_key: str, delete_subtasks: bool = False) -> bool:
        """Supprime une issue"""
        params = {'deleteSubtasks': 'true' if delete_subtasks else 'false'}
        endpoint = f'issue/{issue_key}'
        url = f"{self.client.base_url}/rest/api/3/{endpoint}"

        import requests
        response = requests.delete(url, auth=self.client.auth, params=params)
        return response.status_code in [204, 200]

    def transition_issue(self, issue_key: str, transition_name: str,
                        comment: str = None, resolution: str = None) -> bool:
        """Effectue une transition de workflow"""
        # Récupérer les transitions disponibles
        transitions = self.client.get(f'issue/{issue_key}/transitions')

        if not transitions:
            return False

        # Trouver l'ID de la transition
        transition_id = None
        for t in transitions.get('transitions', []):
            if t['name'].lower() == transition_name.lower():
                transition_id = t['id']
                break

        if not transition_id:
            print(f"Transition '{transition_name}' non trouvée", file=sys.stderr)
            print(f"Transitions disponibles: {[t['name'] for t in transitions.get('transitions', [])]}",
                  file=sys.stderr)
            return False

        # Préparer les données
        transition_data = {
            'transition': {'id': transition_id}
        }

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

        if resolution:
            transition_data['fields'] = {'resolution': {'name': resolution}}

        result = self.client.post(f'issue/{issue_key}/transitions', data=transition_data)
        return result is not None

    def get_transitions(self, issue_key: str) -> List[Dict]:
        """Récupère les transitions disponibles pour une issue"""
        result = self.client.get(f'issue/{issue_key}/transitions')
        return result.get('transitions', []) if result else []

    def assign_issue(self, issue_key: str, account_id: str = None) -> bool:
        """Assigne une issue à un utilisateur (None = automatic)"""
        data = {'accountId': account_id} if account_id else None
        result = self.client.put(f'issue/{issue_key}/assignee', data=data)
        return result is not None

    def clone_issue(self, issue_key: str, summary: str = None) -> Dict:
        """Clone une issue"""
        original = self.get_issue(issue_key)
        if not original:
            return None

        fields = original.get('fields', {})

        clone_summary = summary or f"[CLONE] {fields.get('summary', '')}"

        return self.create_issue(
            project_key=fields['project']['key'],
            summary=clone_summary,
            issue_type=fields['issuetype']['name'],
            description=self._extract_description(fields.get('description')),
            priority=fields.get('priority', {}).get('name') if fields.get('priority') else None,
            labels=fields.get('labels', []),
            components=[c['name'] for c in fields.get('components', [])]
        )

    def _extract_description(self, description_doc: Dict) -> str:
        """Extrait le texte d'une description au format ADF"""
        if not description_doc or not isinstance(description_doc, dict):
            return ""

        text_parts = []
        for content in description_doc.get('content', []):
            if content.get('type') == 'paragraph':
                for item in content.get('content', []):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))

        return ' '.join(text_parts)

    # === COMMENTAIRES ===

    def add_comment(self, issue_key: str, text: str, visibility: Dict = None) -> Dict:
        """Ajoute un commentaire à une issue"""
        comment_data = {
            'body': {
                'type': 'doc',
                'version': 1,
                'content': [{
                    'type': 'paragraph',
                    'content': [{'type': 'text', 'text': text}]
                }]
            }
        }

        if visibility:
            comment_data['visibility'] = visibility

        return self.client.post(f'issue/{issue_key}/comment', data=comment_data)

    def list_comments(self, issue_key: str) -> List[Dict]:
        """Liste les commentaires d'une issue"""
        result = self.client.get(f'issue/{issue_key}/comment')
        return result.get('comments', []) if result else []

    def update_comment(self, issue_key: str, comment_id: str, text: str) -> Dict:
        """Met à jour un commentaire"""
        comment_data = {
            'body': {
                'type': 'doc',
                'version': 1,
                'content': [{
                    'type': 'paragraph',
                    'content': [{'type': 'text', 'text': text}]
                }]
            }
        }
        return self.client.put(f'issue/{issue_key}/comment/{comment_id}', data=comment_data)

    def delete_comment(self, issue_key: str, comment_id: str) -> bool:
        """Supprime un commentaire"""
        return self.client.delete(f'issue/{issue_key}/comment/{comment_id}')

    # === ATTACHMENTS ===

    def list_attachments(self, issue_key: str) -> List[Dict]:
        """Liste les pièces jointes d'une issue"""
        issue = self.get_issue(issue_key, fields=['attachment'])
        return issue.get('fields', {}).get('attachment', []) if issue else []

    def add_attachment(self, issue_key: str, file_path: str) -> Dict:
        """Ajoute une pièce jointe"""
        import requests

        url = f"{self.client.base_url}/rest/api/3/issue/{issue_key}/attachments"

        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {'X-Atlassian-Token': 'no-check'}

            response = requests.post(
                url,
                auth=self.client.auth,
                files=files,
                headers=headers
            )

            if response.status_code in [200, 201]:
                return response.json()
            return None

    def delete_attachment(self, attachment_id: str) -> bool:
        """Supprime une pièce jointe"""
        return self.client.delete(f'attachment/{attachment_id}')

    # === WATCHERS ===

    def add_watcher(self, issue_key: str, account_id: str) -> bool:
        """Ajoute un observateur"""
        result = self.client.post(f'issue/{issue_key}/watchers', data=account_id)
        return result is not None

    def remove_watcher(self, issue_key: str, account_id: str) -> bool:
        """Retire un observateur"""
        endpoint = f'issue/{issue_key}/watchers'
        url = f"{self.client.base_url}/rest/api/3/{endpoint}"

        import requests
        response = requests.delete(
            url,
            auth=self.client.auth,
            params={'accountId': account_id}
        )
        return response.status_code in [204, 200]

    def list_watchers(self, issue_key: str) -> List[Dict]:
        """Liste les observateurs"""
        result = self.client.get(f'issue/{issue_key}/watchers')
        return result.get('watchers', []) if result else []

    # === LIENS ===

    def link_issues(self, issue_key: str, target_key: str, link_type: str = 'Relates') -> Dict:
        """Crée un lien entre deux issues"""
        link_data = {
            'type': {'name': link_type},
            'inwardIssue': {'key': issue_key},
            'outwardIssue': {'key': target_key}
        }
        return self.client.post('issueLink', data=link_data)

    def get_issue_links(self, issue_key: str) -> List[Dict]:
        """Récupère les liens d'une issue"""
        issue = self.get_issue(issue_key, fields=['issuelinks'])
        return issue.get('fields', {}).get('issuelinks', []) if issue else []

    def delete_link(self, link_id: str) -> bool:
        """Supprime un lien entre issues"""
        return self.client.delete(f'issueLink/{link_id}')

    # === RECHERCHE ===

    def search_issues(self, jql: str, fields: List[str] = None, max_results: int = 50) -> List[Dict]:
        """Recherche des issues par JQL"""
        params = {
            'jql': jql,
            'maxResults': max_results
        }
        if fields:
            params['fields'] = ','.join(fields)

        return self.client.get_paginated('search', params=params)


def main():
    parser = argparse.ArgumentParser(description='Gestion des issues Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Créer une issue
    create_parser = subparsers.add_parser('create', help='Créer une issue')
    create_parser.add_argument('project', help='Clé du projet')
    create_parser.add_argument('summary', help='Résumé de l\'issue')
    create_parser.add_argument('--type', default='Task', help='Type d\'issue')
    create_parser.add_argument('--description', help='Description')
    create_parser.add_argument('--priority', help='Priorité')
    create_parser.add_argument('--assignee', help='Account ID de l\'assigné')
    create_parser.add_argument('--labels', nargs='*', help='Labels')
    create_parser.add_argument('--components', nargs='*', help='Composants')

    # Voir une issue
    get_parser = subparsers.add_parser('get', help='Voir une issue')
    get_parser.add_argument('issue_key', help='Clé de l\'issue')
    get_parser.add_argument('--fields', nargs='*', help='Champs à récupérer')

    # Mettre à jour une issue
    update_parser = subparsers.add_parser('update', help='Mettre à jour une issue')
    update_parser.add_argument('issue_key', help='Clé de l\'issue')
    update_parser.add_argument('--summary', help='Nouveau résumé')
    update_parser.add_argument('--description', help='Nouvelle description')
    update_parser.add_argument('--priority', help='Nouvelle priorité')

    # Supprimer une issue
    delete_parser = subparsers.add_parser('delete', help='Supprimer une issue')
    delete_parser.add_argument('issue_key', help='Clé de l\'issue')
    delete_parser.add_argument('--delete-subtasks', action='store_true',
                              help='Supprimer aussi les sous-tâches')
    delete_parser.add_argument('--confirm', action='store_true', help='Confirmer la suppression')

    # Transition
    transition_parser = subparsers.add_parser('transition', help='Changer le statut d\'une issue')
    transition_parser.add_argument('issue_key', help='Clé de l\'issue')
    transition_parser.add_argument('transition', help='Nom de la transition')
    transition_parser.add_argument('--comment', help='Commentaire')
    transition_parser.add_argument('--resolution', help='Résolution')

    # Transitions disponibles
    transitions_parser = subparsers.add_parser('transitions', help='Voir les transitions disponibles')
    transitions_parser.add_argument('issue_key', help='Clé de l\'issue')

    # Assigner
    assign_parser = subparsers.add_parser('assign', help='Assigner une issue')
    assign_parser.add_argument('issue_key', help='Clé de l\'issue')
    assign_parser.add_argument('--account-id', help='Account ID (vide = automatic)')

    # Cloner
    clone_parser = subparsers.add_parser('clone', help='Cloner une issue')
    clone_parser.add_argument('issue_key', help='Clé de l\'issue')
    clone_parser.add_argument('--summary', help='Nouveau résumé')

    # === COMMENTAIRES ===

    comment_add_parser = subparsers.add_parser('comment-add', help='Ajouter un commentaire')
    comment_add_parser.add_argument('issue_key', help='Clé de l\'issue')
    comment_add_parser.add_argument('text', help='Texte du commentaire')

    comment_list_parser = subparsers.add_parser('comment-list', help='Lister les commentaires')
    comment_list_parser.add_argument('issue_key', help='Clé de l\'issue')

    comment_update_parser = subparsers.add_parser('comment-update', help='Mettre à jour un commentaire')
    comment_update_parser.add_argument('issue_key', help='Clé de l\'issue')
    comment_update_parser.add_argument('comment_id', help='ID du commentaire')
    comment_update_parser.add_argument('text', help='Nouveau texte')

    comment_delete_parser = subparsers.add_parser('comment-delete', help='Supprimer un commentaire')
    comment_delete_parser.add_argument('issue_key', help='Clé de l\'issue')
    comment_delete_parser.add_argument('comment_id', help='ID du commentaire')

    # === ATTACHMENTS ===

    attach_list_parser = subparsers.add_parser('attachment-list', help='Lister les pièces jointes')
    attach_list_parser.add_argument('issue_key', help='Clé de l\'issue')

    attach_add_parser = subparsers.add_parser('attachment-add', help='Ajouter une pièce jointe')
    attach_add_parser.add_argument('issue_key', help='Clé de l\'issue')
    attach_add_parser.add_argument('file', help='Chemin du fichier')

    attach_delete_parser = subparsers.add_parser('attachment-delete', help='Supprimer une pièce jointe')
    attach_delete_parser.add_argument('attachment_id', help='ID de la pièce jointe')

    # === WATCHERS ===

    watcher_add_parser = subparsers.add_parser('watcher-add', help='Ajouter un observateur')
    watcher_add_parser.add_argument('issue_key', help='Clé de l\'issue')
    watcher_add_parser.add_argument('account_id', help='Account ID')

    watcher_remove_parser = subparsers.add_parser('watcher-remove', help='Retirer un observateur')
    watcher_remove_parser.add_argument('issue_key', help='Clé de l\'issue')
    watcher_remove_parser.add_argument('account_id', help='Account ID')

    watcher_list_parser = subparsers.add_parser('watcher-list', help='Lister les observateurs')
    watcher_list_parser.add_argument('issue_key', help='Clé de l\'issue')

    # === LIENS ===

    link_parser = subparsers.add_parser('link', help='Lier deux issues')
    link_parser.add_argument('issue_key', help='Clé de l\'issue source')
    link_parser.add_argument('target_key', help='Clé de l\'issue cible')
    link_parser.add_argument('--type', default='Relates', help='Type de lien')

    link_list_parser = subparsers.add_parser('link-list', help='Lister les liens')
    link_list_parser.add_argument('issue_key', help='Clé de l\'issue')

    link_delete_parser = subparsers.add_parser('link-delete', help='Supprimer un lien')
    link_delete_parser.add_argument('link_id', help='ID du lien')

    # === RECHERCHE ===

    search_parser = subparsers.add_parser('search', help='Rechercher des issues')
    search_parser.add_argument('jql', help='Requête JQL')
    search_parser.add_argument('--fields', nargs='*', help='Champs à récupérer')
    search_parser.add_argument('--max', type=int, default=50, help='Nombre max de résultats')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        manager = IssueManager(client)

        if args.command == 'create':
            fields = {}
            if args.labels:
                fields['labels'] = args.labels
            if args.components:
                fields['components'] = [{'name': c} for c in args.components]

            issue = manager.create_issue(
                project_key=args.project,
                summary=args.summary,
                issue_type=args.type,
                description=args.description,
                priority=args.priority,
                assignee=args.assignee,
                labels=args.labels,
                components=args.components
            )

            if issue:
                print(f"✓ Issue créée: {issue['key']}")
                print(f"  URL: {client.base_url}/browse/{issue['key']}")
            else:
                print("✗ Échec de la création", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'get':
            issue = manager.get_issue(args.issue_key, fields=args.fields)
            if issue:
                print(json.dumps(issue, indent=2, ensure_ascii=False))
            else:
                print(f"Issue {args.issue_key} non trouvée", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'update':
            fields = {}
            if args.summary:
                fields['summary'] = args.summary
            if args.description:
                fields['description'] = {
                    'type': 'doc',
                    'version': 1,
                    'content': [{
                        'type': 'paragraph',
                        'content': [{'type': 'text', 'text': args.description}]
                    }]
                }
            if args.priority:
                fields['priority'] = {'name': args.priority}

            if manager.update_issue(args.issue_key, **fields):
                print(f"✓ Issue {args.issue_key} mise à jour")
            else:
                print(f"✗ Échec de la mise à jour", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'delete':
            if not args.confirm:
                response = input(f"⚠ Confirmer la suppression de {args.issue_key} ? (oui/non): ")
                if response.lower() not in ['oui', 'o', 'yes', 'y']:
                    print("Suppression annulée")
                    return

            if manager.delete_issue(args.issue_key, args.delete_subtasks):
                print(f"✓ Issue {args.issue_key} supprimée")
            else:
                print(f"✗ Échec de la suppression", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'transition':
            if manager.transition_issue(args.issue_key, args.transition,
                                       args.comment, args.resolution):
                print(f"✓ Transition '{args.transition}' effectuée sur {args.issue_key}")
            else:
                print(f"✗ Échec de la transition", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'transitions':
            transitions = manager.get_transitions(args.issue_key)
            print(f"\nTransitions disponibles pour {args.issue_key}:")
            for t in transitions:
                print(f"  • {t['name']} (ID: {t['id']})")
                if t.get('to'):
                    print(f"    → Vers: {t['to']['name']}")

        elif args.command == 'assign':
            if manager.assign_issue(args.issue_key, args.account_id):
                assignee = args.account_id or "Automatic"
                print(f"✓ Issue {args.issue_key} assignée à {assignee}")
            else:
                print(f"✗ Échec de l'assignation", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'clone':
            clone = manager.clone_issue(args.issue_key, args.summary)
            if clone:
                print(f"✓ Issue clonée: {clone['key']}")
                print(f"  URL: {client.base_url}/browse/{clone['key']}")
            else:
                print(f"✗ Échec du clonage", file=sys.stderr)
                sys.exit(1)

        # === COMMENTAIRES ===

        elif args.command == 'comment-add':
            comment = manager.add_comment(args.issue_key, args.text)
            if comment:
                print(f"✓ Commentaire ajouté (ID: {comment['id']})")
            else:
                print(f"✗ Échec de l'ajout du commentaire", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'comment-list':
            comments = manager.list_comments(args.issue_key)
            print(f"\nCommentaires de {args.issue_key}:")
            for c in comments:
                author = c.get('author', {}).get('displayName', 'Unknown')
                created = c.get('created', '')
                print(f"\n  [{c['id']}] {author} - {created}")
                # Extraire le texte du commentaire
                body = c.get('body', {})
                if isinstance(body, dict):
                    for content in body.get('content', []):
                        if content.get('type') == 'paragraph':
                            for item in content.get('content', []):
                                if item.get('type') == 'text':
                                    print(f"  {item.get('text', '')}")

        elif args.command == 'comment-update':
            if manager.update_comment(args.issue_key, args.comment_id, args.text):
                print(f"✓ Commentaire {args.comment_id} mis à jour")
            else:
                print(f"✗ Échec de la mise à jour", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'comment-delete':
            if manager.delete_comment(args.issue_key, args.comment_id):
                print(f"✓ Commentaire {args.comment_id} supprimé")
            else:
                print(f"✗ Échec de la suppression", file=sys.stderr)
                sys.exit(1)

        # === ATTACHMENTS ===

        elif args.command == 'attachment-list':
            attachments = manager.list_attachments(args.issue_key)
            print(f"\nPièces jointes de {args.issue_key}:")
            for a in attachments:
                size = a.get('size', 0) / 1024  # KB
                print(f"  • {a.get('filename')} ({size:.1f} KB)")
                print(f"    ID: {a.get('id')}")
                print(f"    Auteur: {a.get('author', {}).get('displayName', 'Unknown')}")

        elif args.command == 'attachment-add':
            result = manager.add_attachment(args.issue_key, args.file)
            if result:
                print(f"✓ Pièce jointe ajoutée")
            else:
                print(f"✗ Échec de l'ajout", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'attachment-delete':
            if manager.delete_attachment(args.attachment_id):
                print(f"✓ Pièce jointe supprimée")
            else:
                print(f"✗ Échec de la suppression", file=sys.stderr)
                sys.exit(1)

        # === WATCHERS ===

        elif args.command == 'watcher-add':
            if manager.add_watcher(args.issue_key, args.account_id):
                print(f"✓ Observateur ajouté")
            else:
                print(f"✗ Échec de l'ajout", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'watcher-remove':
            if manager.remove_watcher(args.issue_key, args.account_id):
                print(f"✓ Observateur retiré")
            else:
                print(f"✗ Échec du retrait", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'watcher-list':
            watchers = manager.list_watchers(args.issue_key)
            print(f"\nObservateurs de {args.issue_key}:")
            for w in watchers:
                print(f"  • {w.get('displayName')} ({w.get('emailAddress', 'N/A')})")

        # === LIENS ===

        elif args.command == 'link':
            if manager.link_issues(args.issue_key, args.target_key, args.type):
                print(f"✓ Lien créé: {args.issue_key} {args.type} {args.target_key}")
            else:
                print(f"✗ Échec de la création du lien", file=sys.stderr)
                sys.exit(1)

        elif args.command == 'link-list':
            links = manager.get_issue_links(args.issue_key)
            print(f"\nLiens de {args.issue_key}:")
            for link in links:
                link_type = link.get('type', {}).get('name', 'Unknown')
                if 'inwardIssue' in link:
                    other = link['inwardIssue']
                    print(f"  • {link_type}: {other['key']} - {other.get('fields', {}).get('summary', '')}")
                elif 'outwardIssue' in link:
                    other = link['outwardIssue']
                    print(f"  • {link_type}: {other['key']} - {other.get('fields', {}).get('summary', '')}")

        elif args.command == 'link-delete':
            if manager.delete_link(args.link_id):
                print(f"✓ Lien supprimé")
            else:
                print(f"✗ Échec de la suppression", file=sys.stderr)
                sys.exit(1)

        # === RECHERCHE ===

        elif args.command == 'search':
            issues = manager.search_issues(args.jql, args.fields, args.max)
            print(f"\nRésultats de recherche ({len(issues)} issues):")
            for issue in issues:
                fields = issue.get('fields', {})
                status = fields.get('status', {}).get('name', 'Unknown')
                print(f"  • {issue['key']}: {fields.get('summary', '')} [{status}]")

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
