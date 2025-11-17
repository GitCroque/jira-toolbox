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
  users       Gestion des utilisateurs (list, search, audit, export, etc.)
  audit       Audit et monitoring (projects, roles, permissions, workflows, groups)
  projects    Gestion des projets (list, get, stats, export, archive, restore)
  reports     Reporting et analytique (project, user, sla, dashboard, export-csv)
  issues      Gestion des issues (create, update, delete, transition, comment, etc.)
  sprints     Gestion des sprints (create, start, close, add-issues, velocity, etc.)
  bulk        Opérations en masse (create, update, delete, transition, import-csv, etc.)
  boards      Gestion des boards (list, create, config, issues, sprints, etc.)
  dashboards  Gestion des dashboards et filtres (list, create, share, favourites, etc.)

Exemples:
  python3 jira_cli.py users list
  python3 jira_cli.py audit projects
  python3 jira_cli.py projects stats PROJECT-KEY
  python3 jira_cli.py reports dashboard
  python3 jira_cli.py issues create PROJ "Issue title" --type Task
  python3 jira_cli.py sprints start 123
  python3 jira_cli.py bulk transition "In Progress" --jql "project = PROJ"
  python3 jira_cli.py boards list --project PROJ
  python3 jira_cli.py dashboards filter-list

Pour plus d'aide sur une commande:
  python3 jira_cli.py issues --help
  python3 jira_cli.py sprints --help
  python3 jira_cli.py bulk --help
        """
    )

    parser.add_argument('tool', choices=['users', 'audit', 'projects', 'reports',
                                        'issues', 'sprints', 'bulk', 'boards', 'dashboards'],
                       help='Outil à utiliser')
    parser.add_argument('args', nargs=argparse.REMAINDER,
                       help='Arguments pour l\'outil')

    args = parser.parse_args()

    # Mapper les outils vers leurs scripts
    tool_map = {
        'users': 'jira_cli/scripts/user_manager.py',
        'audit': 'jira_cli/scripts/audit_tool.py',
        'projects': 'jira_cli/scripts/project_manager.py',
        'reports': 'jira_cli/scripts/reporting.py',
        'issues': 'jira_cli/scripts/issue_manager.py',
        'sprints': 'jira_cli/scripts/sprint_manager.py',
        'bulk': 'jira_cli/scripts/bulk_operations.py',
        'boards': 'jira_cli/scripts/board_manager.py',
        'dashboards': 'jira_cli/scripts/dashboard_manager.py'
    }

    script = tool_map[args.tool]

    # Exécuter le script correspondant avec les arguments
    import subprocess
    cmd = [sys.executable, script] + args.args
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
