# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import json
import os
import re
import sys
from pathlib import Path

# import oauth2
import psutil
# import schemas
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# from test.config import Config

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))

import netifaces
from sqlalchemy import exc

import api.domain.ethernet.models as ethernet_models
import api.domain.ethernet.schemas as ethernet_schemas
import model.models as models
import utils.oauth2 as oauth2
# from api.domain.ethernet import models, schemas
from configs.config import *
from database.db import get_db
from utils.libCom import create_file_config_network

# 
router = APIRouter(
    prefix="/ethernet",
    tags=['Ethernet']
)
# Describe functions before writing code
# /**
# 	 * @description get ethernet
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (EthernetOut)
# 	 */  
@router.post('/', response_model=ethernet_schemas.EthernetOut)
def get_ethernet(id: int, db: Session = Depends(get_db), 
                 current_user: int = Depends(oauth2.get_current_user) ):
    try:
        # ----------------------
        ethernet = db.query(ethernet_models.Ethernet).filter_by(id = id).first()
        # ethernet_list=ethernet.__dict__
        # print(f'ethernet :{ethernet_list}')
        # ----------------------
        # result = db.execute(
        # text(f'select * from user')).all()
        # results_dict = [row._asdict() for row in result]
        # print(f'{results_dict}')
        # ----------------------
        if not ethernet:
            return JSONResponse(content={"detail": f"Ethernet with id: {id} does not exist"}, status_code=status.HTTP_404_NOT_FOUND)
        return ethernet
    except (Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=500, detail="Internal server error")
# Describe functions before writing code
# /**
# 	 * @description update ethernet
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (EthernetOut)
# 	 */  
@router.post("/update/", response_model=ethernet_schemas.EthernetOut)
def update_ethernet(id: int,  updated_ethernet: ethernet_schemas.EthernetCreate,
                    db: Session = Depends(get_db)
                    , current_user: int = Depends(oauth2.get_current_user)):
    try:
    
        # result = db.execute(
        # text('select * from ethernet  where id =:id'), params={'id': id}).all()
        # select * from ethernet INNER JOIN config_information ON config_information.id=ethernet.id_type_ethernet where ethernet.id =:id'
        
        ethernet_query = db.query(ethernet_models.Ethernet).filter_by(id = id)
        if ethernet_query.first() == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Ethernet with id: {id} does not exist")
        id_type_ethernet=updated_ethernet.id_type_ethernet
        
        config_information_query = db.query(models.Config_information).filter_by(id = id_type_ethernet).first()
        if config_information_query == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Ethernet with DHCP/Use Static Ip: {id_type_ethernet} does not exist")
        
        # check dhcp/Use Static Ip
        id_type_ethernet_name=config_information_query.name
        # 
        id_ethernet=id
        namekey=updated_ethernet.namekey
        allow_dns = bool(updated_ethernet.allow_dns)
        ip_address=updated_ethernet.ip_address
        gateway=updated_ethernet.gateway
        dns1=updated_ethernet.dns1
        dns2=updated_ethernet.dns2
        # 
        all_ethernet_query = db.query(ethernet_models.Ethernet).all()
        # 
        pathfile= Config.PATH_FILE_NETWORK_INTERFACE
        # print(f'pathfile: {pathfile}')
        network_interface=dict(id_ethernet=id_ethernet,
                            namekey=namekey,
                            allow_dns=allow_dns,
                            ip_address=ip_address,
                            gateway=gateway,
                            dns1=dns1,
                            dns2=dns2,
                            pathfile=pathfile,
                            id_type_ethernet_name=id_type_ethernet_name
                        )
        try: 
            ethernet_query.update(updated_ethernet.dict(), synchronize_session=False)
        except exc.SQLAlchemyError as err:
            db.rollback()
            if re.match("(.*)Duplicate entry(.*)", err.args[0]):
                
                return JSONResponse(content={"detail": "Duplicate record"}, status_code=409)
        
        create_file_config_network(all_ethernet_query,network_interface,pathfile)
        check_file = os.path.isfile(pathfile)
        
        if check_file == False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Ethernet with 01-netcfg.yaml: does not exist")
            
        db.commit()
        return ethernet_query.first()
    
    except (Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=500, detail="Internal server error")
# Describe functions before writing code
# /**
# 	 * @description get network interface
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data (NetworkBase)
# 	 */ 
@router.post('/ifconfig/', response_model=ethernet_schemas.NetworkBase)
def get_network_interface(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        # result=psutil.net_if_addrs()
        # print(result["Ethernet"])
        # for key, value in result["Ethernet"].items(): 
        #     print(key)
        # ----------------------
        # if not result:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        #                         detail=f"Not find network interface card")
        # network_list=[]
        # for key, value in result.items(): 
        
        #     array_item=[]
        #     for item in value:
        #         array_item.append(str(item))
            
        #     network_list.append({
        #         "interface":key,
        #         "information": array_item
        #     })
        config_information_query = db.query(models.Config_information).filter_by(id_type = 14).\
            filter_by(status = 1).all()
        
        network_list=[]
        interfaceList=netifaces.interfaces()
        # ----------------------------------------------
        for interface in interfaceList:
            result=netifaces.ifaddresses(interface)
            addr=""
            netmask=""
            try:
                addr=result[2][0]['addr']
                netmask=result[2][0]['netmask']
            except (Exception) as err:
                pass
            result=netifaces.gateways()
            Gateway=""
            try:
                for item in result[2]:
                    if item[1]==interface:
                        Gateway=item[0]
            except (Exception) as err:
                pass
            network_list.append({
                "namekey":interface,
                "ip_address":addr,
                "subnet_mask":netmask,
                "gateway":Gateway,
                "mtu":"",
                "dns1":"",
                "dns2":"",
            })
        return {
            "network":network_list,
            "mode":config_information_query
        }
    except (Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=500, detail="Internal server error")