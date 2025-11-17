#!/usr/bin/env python3
"""
Jira CLI - Point d'entrée principal
Permet d'accéder à tous les outils depuis une seule commande
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Jira CLI Toolbox - Administration Jira Cloud',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commandes disponibles:
  users      Gestion des utilisateurs (list, search, audit, export, etc.)
  audit      Audit et monitoring (projects, roles, permissions, workflows, groups)
  projects   Gestion des projets (list, get, stats, export, archive, restore)
  reports    Reporting et analytique (project, user, sla, dashboard, export-csv)

Exemples:
  python3 jira_cli.py users list
  python3 jira_cli.py audit projects
  python3 jira_cli.py projects stats PROJECT-KEY
  python3 jira_cli.py reports dashboard

Pour plus d'aide sur une commande:
  python3 jira_cli.py users --help
  python3 jira_cli.py audit --help
        """
    )

    parser.add_argument('tool', choices=['users', 'audit', 'projects', 'reports'],
                       help='Outil à utiliser')
    parser.add_argument('args', nargs=argparse.REMAINDER,
                       help='Arguments pour l\'outil')

    args = parser.parse_args()

    # Mapper les outils vers leurs scripts
    tool_map = {
        'users': 'jira_cli/scripts/user_manager.py',
        'audit': 'jira_cli/scripts/audit_tool.py',
        'projects': 'jira_cli/scripts/project_manager.py',
        'reports': 'jira_cli/scripts/reporting.py'
    }

    script = tool_map[args.tool]

    # Exécuter le script correspondant avec les arguments
    import subprocess
    cmd = [sys.executable, script] + args.args
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
