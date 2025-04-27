from typing import Optional
import routeros_api
from fastapi import HTTPException

class MikrotikAPI:
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.connection = None

    def connect(self):
        try:
            self.connection = routeros_api.RouterOsApiPool(
                self.host,
                username=self.username,
                password=self.password,
                plaintext_login=True
            )
            return self.connection.get_api()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")

    def add_pppoe_user(self, username: str, password: str, speed_limit: Optional[float] = None):
        try:
            api = self.connect()
            ppp = api.get_resource('/ppp/secret')
            
            user_data = {
                'name': username,
                'password': password,
                'service': 'pppoe',
            }
            
            if speed_limit:
                user_data['rate-limit'] = f"{speed_limit}M/{speed_limit}M"
            
            ppp.add(**user_data)
            api.close()
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add PPPoE user: {str(e)}")

    def get_active_connections(self):
        try:
            api = self.connect()
            active = api.get_resource('/ppp/active').get()
            api.close()
            return active
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get active connections: {str(e)}")

    def remove_pppoe_user(self, username: str):
        try:
            api = self.connect()
            ppp = api.get_resource('/ppp/secret')
            secrets = ppp.get(name=username)
            
            if secrets:
                ppp.remove(id=secrets[0]['id'])
                api.close()
                return True
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to remove PPPoE user: {str(e)}")

    def update_user_speed(self, username: str, speed_limit: float):
        try:
            api = self.connect()
            ppp = api.get_resource('/ppp/secret')
            secrets = ppp.get(name=username)
            
            if secrets:
                ppp.set(id=secrets[0]['id'], rate_limit=f"{speed_limit}M/{speed_limit}M")
                api.close()
                return True
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update user speed: {str(e)}")