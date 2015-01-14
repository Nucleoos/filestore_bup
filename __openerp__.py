# -*- coding: utf-8 -*-
##############################################################################
#
#    filestore_bup module for OpenERP, A bup backend for Odoo filestore, to benefit from deduplication and versionning of files
#    Copyright (C) 2015 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of filestore_bup
#
#    filestore_bup is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    filestore_bup is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Filestore Bup',
    'version': '1.0',
    'category': 'Custom',
    'description': """A bup backend for Odoo filestore, to benefit from deduplication and versionning of files""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': ['base'],
    'init_xml': [],
    'images': [],
    'update_xml': [
    ],
    'demo_xml': [],
    'test': [],
    'external_dependancies': {'bin': ['bup']},
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
