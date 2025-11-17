#!/usr/bin/env python3
"""
Script d'audit et de monitoring Jira Cloud
Permet d'auditer les permissions, les projets, les schémas
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.jira_client import JiraClient


class AuditTool:
    """Outil d'audit Jira"""

    def __init__(self, client: JiraClient):
        self.client = client

    def audit_projects(self) -> Dict:
        """Audit de tous les projets"""
        projects = self.client.get_paginated('project/search')

        audit_data = {
            'total_projects': len(projects),
            'by_type': defaultdict(int),
            'by_style': defaultdict(int),
            'projects': []
        }

        for project in projects:
            proj_data = {
                'key': project.get('key'),
                'name': project.get('name'),
                'projectTypeKey': project.get('projectTypeKey'),
                'style': project.get('style'),
                'lead': project.get('lead', {}).get('displayName'),
                'description': project.get('description', '')[:100] if project.get('description') else ''
            }

            audit_data['projects'].append(proj_data)
            audit_data['by_type'][project.get('projectTypeKey', 'unknown')] += 1
            audit_data['by_style'][project.get('style', 'unknown')] += 1

        audit_data['by_type'] = dict(audit_data['by_type'])
        audit_data['by_style'] = dict(audit_data['by_style'])
        audit_data['audit_date'] = datetime.now().isoformat()

        return audit_data

    def audit_project_roles(self, project_key: str) -> Dict:
        """Audit des rôles d'un projet"""
        roles = self.client.get(f'project/{project_key}/role')

        role_details = {}
        if roles:
            for role_name, role_url in roles.items():
                # Extraire l'ID du rôle de l'URL
                role_id = role_url.split('/')[-1]
                role_info = self.client.get(f'project/{project_key}/role/{role_id}')

                if role_info:
                    actors = []
                    for actor in role_info.get('actors', []):
                        actors.append({
                            'type': actor.get('type'),
                            'name': actor.get('displayName') or actor.get('name'),
                            'actorUser': actor.get('actorUser', {}).get('accountId') if actor.get('actorUser') else None
                        })

                    role_details[role_name] = {
                        'id': role_info.get('id'),
                        'description': role_info.get('description'),
                        'actors': actors,
                        'actor_count': len(actors)
                    }

        return {
            'project_key': project_key,
            'roles': role_details,
            'total_roles': len(role_details),
            'audit_date': datetime.now().isoformat()
        }

    def audit_permissions(self) -> Dict:
        """Audit des schémas de permissions"""
        # Récupère tous les schémas de permissions
        permission_schemes = self.client.get_paginated('permissionscheme')

        schemes_data = []
        for scheme in permission_schemes:
            scheme_id = scheme.get('id')
            # Détails du schéma
            details = self.client.get(f'permissionscheme/{scheme_id}')

            if details:
                schemes_data.append({
                    'id': scheme_id,
                    'name': details.get('name'),
                    'description': details.get('description'),
                    'permissions_count': len(details.get('permissions', []))
                })

        return {
            'total_schemes': len(schemes_data),
            'schemes': schemes_data,
            'audit_date': datetime.now().isoformat()
        }

    def audit_workflows(self) -> Dict:
        """Audit des workflows"""
        workflows = self.client.get_paginated('workflow/search')

        workflow_data = {
            'total_workflows': len(workflows),
            'workflows': []
        }

        for wf in workflows:
            workflow_data['workflows'].append({
                'name': wf.get('id', {}).get('name'),
                'description': wf.get('description', ''),
                'is_default': wf.get('isDefault', False),
                'statuses_count': len(wf.get('statuses', []))
            })

        workflow_data['audit_date'] = datetime.now().isoformat()
        return workflow_data

    def audit_groups(self) -> Dict:
        """Audit des groupes"""
        groups = self.client.get_paginated('group/bulk')

        group_data = {
            'total_groups': len(groups),
            'groups': []
        }

        for group in groups:
            group_name = group.get('name')

            # Récupérer les membres du groupe
            members = self.client.get_paginated('group/member',
                                               params={'groupname': group_name})

            group_data['groups'].append({
                'name': group_name,
                'groupId': group.get('groupId'),
                'member_count': len(members)
            })

        group_data['audit_date'] = datetime.now().isoformat()
        return group_data

    def check_project_security(self, project_key: str) -> Dict:
        """Vérifie la sécurité d'un projet"""
        security_levels = []

        # Récupérer le schéma de sécurité du projet
        project = self.client.get(f'project/{project_key}')

        security_data = {
            'project_key': project_key,
            'has_security_scheme': False,
            'security_levels': security_levels,
            'issues_with_security': 0
        }

        # Note: L'API de sécurité est limitée sur Jira Cloud
        # Cette partie nécessite des permissions spécifiques

        return security_data

    def get_audit_log(self, from_date: str = None, to_date: str = None) -> List[Dict]:
        """
        Récupère les logs d'audit
        Note: Nécessite Jira Cloud Premium
        """
        params = {}

        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date

        # L'API d'audit nécessite des permissions premium
        try:
            audit_records = self.client.get('auditing/record', params=params)
            return audit_records.get('records', []) if audit_records else []
        except:
            print("⚠ Les logs d'audit nécessitent Jira Cloud Premium", file=sys.stderr)
            return []


def main():
    parser = argparse.ArgumentParser(description='Audit et monitoring Jira Cloud')
    parser.add_argument('--config', help='Fichier de configuration')

    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Audit des projets
    projects_parser = subparsers.add_parser('projects', help='Auditer tous les projets')
    projects_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Audit des rôles d'un projet
    roles_parser = subparsers.add_parser('roles', help='Auditer les rôles d\'un projet')
    roles_parser.add_argument('project_key', help='Clé du projet')
    roles_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Audit des permissions
    perms_parser = subparsers.add_parser('permissions', help='Auditer les schémas de permissions')
    perms_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Audit des workflows
    wf_parser = subparsers.add_parser('workflows', help='Auditer les workflows')
    wf_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Audit des groupes
    groups_parser = subparsers.add_parser('groups', help='Auditer les groupes')
    groups_parser.add_argument('--output', help='Fichier de sortie JSON')

    # Audit complet
    full_parser = subparsers.add_parser('full', help='Audit complet')
    full_parser.add_argument('--output', help='Répertoire de sortie')

    # Logs d'audit
    logs_parser = subparsers.add_parser('logs', help='Récupérer les logs d\'audit')
    logs_parser.add_argument('--from', dest='from_date', help='Date de début (ISO format)')
    logs_parser.add_argument('--to', dest='to_date', help='Date de fin (ISO format)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = JiraClient(args.config)
        audit = AuditTool(client)

        if args.command == 'projects':
            data = audit.audit_projects()

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✓ Audit exporté vers {args.output}")
            else:
                print("\n=== AUDIT DES PROJETS ===")
                print(f"Total: {data['total_projects']} projets")
                print(f"\nPar type:")
                for ptype, count in data['by_type'].items():
                    print(f"  • {ptype}: {count}")
                print(f"\nPar style:")
                for style, count in data['by_style'].items():
                    print(f"  • {style}: {count}")

        elif args.command == 'roles':
            data = audit.audit_project_roles(args.project_key)

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✓ Audit exporté vers {args.output}")
            else:
                print(f"\n=== RÔLES DU PROJET {args.project_key} ===")
                for role_name, role_info in data['roles'].items():
                    print(f"\n{role_name}:")
                    print(f"  Description: {role_info['description']}")
                    print(f"  Acteurs ({role_info['actor_count']}):")
                    for actor in role_info['actors']:
                        print(f"    • {actor['name']} ({actor['type']})")

        elif args.command == 'permissions':
            data = audit.audit_permissions()

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✓ Audit exporté vers {args.output}")
            else:
                print(f"\n=== SCHÉMAS DE PERMISSIONS ===")
                print(f"Total: {data['total_schemes']} schémas")
                for scheme in data['schemes']:
                    print(f"\n  • {scheme['name']}")
                    print(f"    ID: {scheme['id']}")
                    print(f"    Permissions: {scheme['permissions_count']}")

        elif args.command == 'workflows':
            data = audit.audit_workflows()

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✓ Audit exporté vers {args.output}")
            else:
                print(f"\n=== WORKFLOWS ===")
                print(f"Total: {data['total_workflows']} workflows")
                for wf in data['workflows']:
                    default = " [DEFAULT]" if wf['is_default'] else ""
                    print(f"\n  • {wf['name']}{default}")
                    print(f"    Statuts: {wf['statuses_count']}")

        elif args.command == 'groups':
            data = audit.audit_groups()

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"✓ Audit exporté vers {args.output}")
            else:
                print(f"\n=== GROUPES ===")
                print(f"Total: {data['total_groups']} groupes")
                for group in data['groups']:
                    print(f"  • {group['name']}: {group['member_count']} membres")

        elif args.command == 'full':
            print("Audit complet en cours...")

            output_dir = args.output or f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(output_dir, exist_ok=True)

            # Audit projects
            print("  • Audit des projets...")
            with open(f"{output_dir}/projects.json", 'w') as f:
                json.dump(audit.audit_projects(), f, indent=2, ensure_ascii=False)

            # Audit permissions
            print("  • Audit des permissions...")
            with open(f"{output_dir}/permissions.json", 'w') as f:
                json.dump(audit.audit_permissions(), f, indent=2, ensure_ascii=False)

            # Audit workflows
            print("  • Audit des workflows...")
            with open(f"{output_dir}/workflows.json", 'w') as f:
                json.dump(audit.audit_workflows(), f, indent=2, ensure_ascii=False)

            # Audit groups
            print("  • Audit des groupes...")
            with open(f"{output_dir}/groups.json", 'w') as f:
                json.dump(audit.audit_groups(), f, indent=2, ensure_ascii=False)

            print(f"\n✓ Audit complet exporté vers {output_dir}/")

        elif args.command == 'logs':
            logs = audit.get_audit_log(args.from_date, args.to_date)
            print(json.dumps(logs, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
