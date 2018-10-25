# elastic_stack_tools
Scripts to export Elastic Stack data

# Files
- backup_elastic_pipelines.sh	- Export pipelines from the local ES node.
- backup_kibana_objects.sh	- Export Kibana objects
- elastic_templates.py - Update all templates to optimize for spinning disks.  Also inject a meta field with the template name to know which template created a given index.
