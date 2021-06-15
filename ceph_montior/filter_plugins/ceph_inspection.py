#!/usr/bin/python


from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible.module_utils.six import iteritems
import json


class ceph(object):
    
    @staticmethod
    def _conver_list(data_str):
         return data_str.split()

    @staticmethod
    def _conver_int(list_str):
        return list(map(int, list_str))
    
    @staticmethod
    def _conver_float(list_str):
        return list(map(float, list_str))

    @staticmethod
    def conver_cluster_health(health):
        cluster_health_dict=dict(status='OK', info='ceph cluster OK', meta='{}'.format(health))
        health_list = health.split('_')
        if health_list[1] == 'WARN':
           cluster_health_dict['status'] = 'WARNNING'
           cluster_health_dict['info'] = 'ceph cluster warnning'
           return cluster_health_dict
        if health_list[1] == 'ERR':
           cluster_health_dict['status'] = 'ERROR'
           cluster_health_dict['info'] = 'ceph cluster error'
        return cluster_health_dict
  
    @staticmethod
    def conver_ceph_osd_total_up_in(status):
        status_list = ceph._conver_int(status.split())
        #[total, up, in]
        # if status_list[0] == status_list[1] and status_list[0] == status_list[2]:
        #   return True
        return status_list

    @staticmethod
    def conver_ceph_osd_rate(rate):
        # If the osd usage rate is less than or equal to 80, return True, 
        # as long as there is one greater than 80, return False 
        ceph_osd_rate_dict=dict(status='OK', info='osd used rate is normal', meta='{}'.format(rate))
        if all(osd_rate <= 80 for osd_rate in ceph._conver_float(ceph._conver_list(rate))):
           return ceph_osd_rate_dict
        ceph_osd_rate_dict['status'] = 'WARNNING'
        ceph_osd_rate_dict['info'] = 'osd usage is greater than 80%'
        return ceph_osd_rate_dict

    @staticmethod
    def conver_ceph_osd_pg_blance(pg_blance):
         # If the number of pg is greater than or equal to 150 and less than or equal to 300, it is true; 
         # otherwise, it is flase
         ceph_osd_pg_blance_dict=dict(status='OK', info='pg load balancing is normal', meta='{}'.format(pg_blance))
         if all(pg_blance >= 150 and pg_blance <= 300 for pg_blance in ceph._conver_float(ceph._conver_list(pg_blance))):
            return ceph_osd_pg_blance_dict
         ceph_osd_pg_blance_dict['status'] = 'WARNNING'
         ceph_osd_pg_blance_dict['info'] = 'pg load is not balanced; because Small and 150 or greater than 300'
         return ceph_osd_pg_blance_dict
     
    @staticmethod
    def conver_ceph_osd_blance(osd_blance):
        ceph_osd_blance_dict=dict(status='WARNNING',  info='osd not load balancing; because Maximum and minimum difference 15%', \
				  meta='hdd:{0} ssd:{1}'.format(osd_blance[1],osd_blance[0]))
        if osd_blance[0]:
           osd_ssd = ceph._conver_float(ceph._conver_list(osd_blance[0]))
           if max(osd_ssd) - min(osd_ssd) > 15:
              return ceph_osd_blance_dict

        if osd_blance[1]:
           osd_hdd = ceph._conver_float(ceph._conver_list(osd_blance[1]))
           if max(osd_hdd) - min(osd_hdd) > 15:
              return ceph_osd_blance_dict
        ceph_osd_blance_dict['status'] = 'OK'
        ceph_osd_blance_dict['info'] = 'osd load balancing is normal'
        return ceph_osd_blance_dict 

    @staticmethod
    def conver_osd_status(osd_status):
        osd_status_dict=dict(status='OK', info='osd status is normal', meta='{}'.format(osd_status))
        if osd_status == '[]':
           return osd_status_dict
        osd_status_dict['status'] = 'WARNNING'
        osd_status_dict['info'] = 'osd status is down'
        return osd_status_dict

    @staticmethod
    def conver_ceph_dict(ceph_dict_data):
        for v in ceph_dict_data['ceph']['meta'].values():  
            if v['status'] != 'OK':
               ceph_dict_data['ceph']['info'].append(v['info'])
               ceph_dict_data['ceph']['status'] = 'WARNNING'
        if ceph_dict_data['ceph']['status'] == 'WARNNING':
           ceph_dict_data['ceph']['info'] = '|'.join( ceph_dict_data['ceph']['info'])
           return ceph_dict_data
        ceph_dict_data['ceph']['status'] = 'OK'
        ceph_dict_data['ceph']['info'] = 'ceph cluster is normal'
        return ceph_dict_data

    @staticmethod
    def conver_res_status(res):
        # If the collected data is empty, exit
        if res == '[]':
           raise ValueError('collected data is empty: {}'.format(res))
        return 1
      
    @staticmethod
    def ceph_overview_filter(data):
        ceph_dict = dict(ceph=dict(status=None, info=[], meta=dict()))
        ceph_data_dict = json.loads(data)
        if ceph.conver_res_status(ceph_data_dict['cluster_health']):
           ceph_dict['ceph']['meta']['cluster_health'] = ceph.conver_cluster_health(ceph_data_dict['cluster_health'])           
        if ceph.conver_res_status(ceph_data_dict['osd_used_rate']):
           ceph_dict['ceph']['meta']['osd_used_rate'] = ceph.conver_ceph_osd_rate(ceph_data_dict['osd_used_rate'])
        if ceph.conver_res_status(ceph_data_dict['osd_pg_num']):
           ceph_dict['ceph']['meta']['osd_pg_balance'] = ceph.conver_ceph_osd_pg_blance(ceph_data_dict['osd_pg_num'])
        if ceph.conver_res_status(ceph_data_dict['osd_ssd_balance'] or ceph_data_dict['osd_hdd_balance']):
           ceph_dict['ceph']['meta']['osd_blance'] = ceph.conver_ceph_osd_blance([ceph_data_dict['osd_ssd_balance'], ceph_data_dict['osd_hdd_balance']])
        ceph_dict['ceph']['meta']['osd_status'] = ceph.conver_osd_status(ceph_data_dict['osd_status'])         
        return ceph.conver_ceph_dict(ceph_dict)


class FilterModule(object):
    """
    Filters for working with output from ceph_data_json
    """

    def filters(self):
        return {
            'ceph_overview_filter': ceph.ceph_overview_filter,
        }
