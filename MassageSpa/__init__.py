"""
Package initializer for the Django project.

This project uses SQLite by default for local development. No DB adapter shim is required.
If you later enable MariaDB and want to use PyMySQL, add the pymysql shim back here:

import pymysql
pymysql.install_as_MySQLdb()

"""

