#!/usr/bin/python3 -u
"""
Modulo de trabajo con la BD GDA
"""

from sqlalchemy import create_engine
from sqlalchemy import text
from spy import Config
from collections import defaultdict
from spy_log import log
#import MySQLdb

# ------------------------------------------------------------------------------
class DLGDB:


    def __init__(self, modo='local', server='comms'):

        self.datasource = ''
        self.engine = ''
        self.conn = ''
        self.connected = False
        self.server = server

        if modo == 'spymovil':
            self.url = Config['BDATOS']['url_gda_spymovil']
        elif modo == 'local':
            self.url = Config['BDATOS']['url_gda_local']
        elif modo == 'ute':
            self.url = Config['BDATOS']['url_dlgdb_ute']
        return


    def connect(self, tag='DLGDB'):
        """
        Retorna True/False si es posible generar una conexion a la bd GDA
        """

        if self.connected:
            return self.connected

        try:
            self.engine = create_engine(self.url)
        except Exception as err_var:
            self.connected = False
            log(module=__name__, server=self.server, function='connect', msg='ERROR_{}: engine NOT created. ABORT !!'.format(tag))
            log(module=__name__, server=self.server, function='connect', msg='ERROR: EXCEPTION_{0} {1}'.format(tag, err_var))
            exit(1)

        try:
            self.conn = self.engine.connect()
            self.connected = True
        except Exception as err_var:
            self.connected = False
            log(module=__name__, server=self.server, function='connect', msg='ERROR_{}: NOT connected. ABORT !!'.format(tag))
            log(module=__name__, server=self.server, function='connect', msg='ERROR: EXCEPTION_{0} {1}'.format(tag, err_var))
            exit(1)

        return self.connected


    def read_all_conf(self, dlgid, tag='DLGDB' ):
        '''
        Leo la configuracion desde DLGDB
                +----------+---------------+------------------------+----------+
                | canal    | parametro     | value                  | param_id |
                +----------+---------------+------------------------+----------+
                | BASE     | RESET         | 0                      |      899 |
                | BASE     | UID           | 304632333433180f000500 |      899 |
                | BASE     | TPOLL         | 60                     |      899 |
                | BASE     | COMMITED_CONF |                        |      899 |
                | BASE     | IMEI          | 860585004331632        |      899 |

                EL diccionario lo manejo con 2 claves para poder usar el metodo get y tener
                un valor por default en caso de que no tenga alguna clave
        '''
        log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, level='SELECT', msg='start_{}'.format(tag))

        if not self.connect(tag):
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{}: can\'t connect !!'.format(tag))
            return

        sql = "SELECT dlgid, magName, tbMCol, disp FROM tbDlgParserConf"
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{0}: SQLQUERY: {1}'.format(tag, sql))
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{0}: EXCEPTION {1}'.format(tag, err_var))
            return False

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))
            return False

        results = rp.fetchall()
        d = defaultdict(dict)
        for row in results:
            id, mag_name, tbm_col, disp = row
            if id not in d.keys():
                d[id] = {}
            if mag_name not in d[id].keys():
                d[id][mag_name] = {}
            d[id][mag_name]['TBMCOL'] = tbm_col
            d[id][mag_name]['DISP'] = disp
            #log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, level='SELECT', msg='BD_{0} conf: [{1}][{2}][{3}][{4}]'.format( tag, id, mag_name, tbm_col, disp))

        return d


    def read_dlg_conf(self, dlgid, tag='DLGDB'):
        '''
        Leo la configuracion desde DLGDB
                +----------+---------------+------------------------+----------+
                | canal    | parametro     | value                  | param_id |
                +----------+---------------+------------------------+----------+
                | BASE     | RESET         | 0                      |      899 |
                | BASE     | UID           | 304632333433180f000500 |      899 |
                | BASE     | TPOLL         | 60                     |      899 |
                | BASE     | COMMITED_CONF |                        |      899 |
                | BASE     | IMEI          | 860585004331632        |      899 |

                EL diccionario lo manejo con 2 claves para poder usar el metodo get y tener
                un valor por default en caso de que no tenga alguna clave
        '''
        log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, level='SELECT', msg='start_{}'.format(tag))

        if not self.connect(tag):
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{}: can\'t connect !!'.format(tag))
            return

        sql = "SELECT magName, tbMCol, disp FROM tbDlgParserConf WHERE dlgId = '{}'".format (dlgid)
        try:
            query = text(sql)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{0}: SQLQUERY: {1}'.format(tag, sql))
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, msg='ERROR_{0}: EXCEPTION {1}'.format(tag, err_var))
            return False

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))
            return False

        results = rp.fetchall()
        d = defaultdict(dict)
        for row in results:
            mag_name, tbm_col, disp = row
            d[mag_name] = ( tbm_col, disp,)
            log(module=__name__, server=self.server, function='read_dlg_conf', dlgid=dlgid, level='SELECT', msg='BD_{0} conf: [{1}][{2}][{3}]'.format( tag, mag_name, tbm_col, disp))

        return d


    def insert_data_line(self,dlgid, d, d_parsConf, bd, tag='DLGDB'):
        '''
        En este caso (dlgdb, UTE), recibo 2 diccionarios:
        uno es d que contiene para el datalogger dado las claves NOMBRE_MAG y los valores
        otro es d_parsConf que tiene todos los dataloggers de UTE con el nombre de magnitud, posicion y disponibilidad.
        Este d no debo tocarlo !!!.
        Recorro el diccionario d y a c/magnitud le agrego el TBMCOL y DISP.
        Luego hago con este una lista para poder armar el query.

        Inserto en las 2 tablas. datos, online

        '''
        if not self.connect():
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{}: can\'t connect!!'.format(tag))
            exit(0)

        '''
        d_q = dict()   
        # Recorro las claves del diccionario con los datos.
        for key in d.keys():
            # Si la clave (pA) tiene una entrada en parsConf
            if key in d_parsConf[dlgid].keys():
                # Voy creando un diccionario con la clave, valor, tbcol, disp.
                d_q[key] = {}
                d_q[key]['VALUE'] = d[key]
                d_q[key]['TBMCOL'] = d_parsConf[dlgid][key]['TBMCOL']
                d_q[key]['DISP'] = d_parsConf[dlgid][key]['DISP']
        '''
        data = list()
        for key in d.keys():
            # Si la clave (pA) tiene una entrada en parsConf
            if key in d_parsConf[dlgid].keys():
                # Voy creando una entrada con la clave, valor, tbcol, disp.
                mag_name = key
                val = d[mag_name]
                col = d_parsConf[dlgid][mag_name]['TBMCOL']
                disp = d_parsConf[dlgid][mag_name]['DISP']
                data.insert( (mag_name,val,col,disp,))

        # Tengo c/elemento en una lista por lo que puedo acceder ordenadamente a la secuencia.
        # Armo el insert.
        sql_main = 'INSERT INTO tbMain (dlgId, fechaHoraData, fechaHoraSys '
        sql_online = 'INSERT INTO tbMainOnline (dlgId, fechaHoraData, fechaHoraSys '
        # Variables:
        for ( mag_name,val,col,disp ) in data:
            sql_main += 'mag{},disp{} '.format(col)
            sql_online += 'mag{},disp{} '.format(col)

        # Valores
        sql_main += ') VALUES ( {0},{1},now() '.format(dlgid, d['timestamp'])
        sql_online += ') VALUES ( {0},{1},now() '.format(dlgid, d['timestamp'])

        for ( mag_name,val,col,disp ) in data:
            sql_main += '{},{} '.format(val,disp)
            sql_online += '{},{} '.format(val, disp)

        # Tail
        sql_main += ')'
        sql_online += ')'

        print("SQL_MAIN=[{}]".format(sql_main))
        print("SQL_ONLINE=[{}]".format(sql_online))
        return True

        errors = 0

        # main
        try:
            query = text(sql_main)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{0}: SQLQUERY: {1}'.format(tag, sql_main))
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{0}: EXCEPTION {1}'.format(tag, err_var))

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            if 'Duplicate entry' in str(err_var):
                # Los duplicados no hacen nada malo. Se da mucho en testing.
                log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='WARN_{}: Duplicated Key'.format(tag))
            else:
                log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))

        # online
        try:
            query = text(sql_online)
        except Exception as err_var:
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{0}: SQLQUERY: {1}'.format(tag, sql_online))
            log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='ERROR_{0}: EXCEPTION {1}'.format(tag, err_var))

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            if 'Duplicate entry' in str(err_var):
                # Los duplicados no hacen nada malo. Se da mucho en testing.
                log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid, msg='WARN_{}: Duplicated Key'.format(tag))
            else:
                log(module=__name__, server=self.server, function='insert_data_line', dlgid=dlgid,msg='ERROR_{}: exec EXCEPTION {}'.format(tag, err_var))

        if errors > 0:
            return False
        else:
            return True


if __name__ == '__main__':
    bd = DLGDB(modo='ute', server='process')
    d = bd.read_all_conf(dlgid='DLG', tag='DLGDB')
    print(d)
    print('Ahora DEF400ś')
    print(d['DEF400'])
