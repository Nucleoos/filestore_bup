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

import os
import subprocess
from openerp import models, fields
from openerp.osv import fields as old_fields
from openerp import SUPERUSER_ID
from openerp.tools import config


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _bup_command(self, cr, uid, command, arguments=None, data=None, path=None, context=None):
        if arguments is None:
            arguments = []
        if path is None:
            path = self._bup_repo_path(cr, uid, context=context)

        command = [
            'bup',
            '--bup-dir=%s' % path,
            command,
        ] + arguments
        sub_proc = subprocess.Popen(' '.join(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result_stdout, result_stderr = sub_proc.communicate(data)
        sub_proc.stdin.close()

        return result_stdout, result_stderr

    def _bup_repo_path(self, cr, uid, context=None):
        location = self._storage(cr, uid, context=context)
        if not location.startswith('bup'):
            location = ''

        # Default path
        path = config['data_dir'] + '/filestore.bup'
        if len(location) > 3:
            # Custom path
            path = location[4:]

        # Check if the bup repo exists, create it instead
        if not os.path.exists(path + '/config'):
            self._bup_command(cr, uid, 'init', path=path, context=context)

        return path

    def _get_file_branch_name(self, cr, uid, attachment_id, context=None):
        return '%s/%s' % (cr.dbname, attachment_id)

    def _get_file_contents(self, cr, uid, fname, context=None):
        result_stdout, result_stderr = self._bup_command(cr, uid, 'join', arguments=[fname], context=context)
        return result_stdout

    def _data_get(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for attachment in self.browse(cr, uid, ids, context=context):
            # Check if we use bup for this file
            if attachment.store_fname and not attachment.store_fname.startswith(cr.dbname + '/'):
                # Read from standard, if the file is not stored in the bup repo
                res[attachment.id] = super(IrAttachment, self)._data_get(cr, uid, [attachment.id], name, arg, context=None)[attachment.id]
            else:
                # Read the file from bup
                res[attachment.id] = self._get_file_contents(cr, uid, self._get_file_branch_name(cr, uid, attachment.id, context=context))

        return res

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # Check if we use bup for this file
        location = self._storage(cr, uid, context=context)
        if not location.startswith('bup'):
            return super(IrAttachment, self)._data_set(cr, uid, id, name, value, arg, context=None)

        attachment = self.browse(cr, uid, id, context=context)
        fname = self._get_file_branch_name(cr, uid, attachment.id, context=context)
        file_contents = value.decode('base64')
        file_size = len(file_contents)

        # Write the file into bup
        self._bup_command(cr, uid, 'split', arguments=['-n %s' % fname], data=file_contents, context=context)

        return super(IrAttachment, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size, 'db_datas': False}, context=context)

    _columns = {
        # Override the field to be able to use attachment's id when storing data (not passed to _file_* methods)
        'datas': old_fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    }

    def _file_read(self, cr, uid, fname, bin_size=False):
        # Check if we use bup for this file
        if not fname.startswith('bup:'):
            return super(IrAttachment, self)._file_read(cr, uid, fname, bin_size=bin_size)
        # Do nothing when using bup, as we overriden the function field

    def _file_write(self, cr, uid, value):
        # Check if we use bup for this file
        location = self._storage(cr, uid)
        if not location.startswith('bup'):
            return super(IrAttachment, self)._file_write(cr, uid, value)
        # Do nothing when using bup, as we overriden the function field

    def _file_delete(self, cr, uid, fname):
        # Check if we use bup for this file
        if not fname.startswith('bup:'):
            return super(IrAttachment, self)._file_delete(cr, uid, fname)
        # Do nothing when using bup, as we overriden the function field

    def unlink(self, cr, uid, ids, context=None):
        # Delete the file in the bup repo
        for attachment in self.browse(cr, uid, ids, context=context):
            if attachment.store_fname and attachment.store_fname.startswith(cr.dbname + '/'):
                # Use git, as bup doesn't have a command to drop a branch
                command = [
                    'git',
                    '--git-dir=%s' % self._bup_repo_path(cr, uid, context=context),
                    'branch',
                    '-D %s' % self._get_file_branch_name(cr, uid, attachment.id, context=context),
                ]
                sub_proc = subprocess.Popen(' '.join(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                result_stdout, result_stderr = sub_proc.communicate()
                sub_proc.stdin.close()

        return super(IrAttachment, self).unlink(cr, uid, ids, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
