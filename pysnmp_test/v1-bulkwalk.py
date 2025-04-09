import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

async def run():
    snmpEngine = SnmpEngine()

    objects = bulk_walk_cmd(
            snmpEngine,
            CommunityData("public"),
            await UdpTransportTarget.create(("192.168.56.101", 161)),
            ContextData(),
            0,
            1,
            # ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2')),
            ObjectType(ObjectIdentity('.1.3.6.1.2.1.4.20')),
            lexicographicMode = False
        )

    async for errorIndication, errorStatus, errorIndex, varBinds in objects:
        if errorIndication:
            print(f"Error: {errorIndication}")
            break
        elif errorStatus:
            print(f"{errorStatus.prettyPrint()} at {errorIndex}")
            break
        else:
            for varBind in varBinds:
                print(" = ".join([x.prettyPrint() for x in varBind]))
    
    snmpEngine.close_dispatcher()


asyncio.run(run())