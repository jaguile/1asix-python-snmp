# PySNMP. Introducció

## Creació de l'entorn Python

Genero entorn virtual (*Python Virtual Environment*) i l'activo:

```bash
$ python -m venv .venv
$ source .venv/bin/activate
```

Instal·lo el paquet [pysnmp](https://github.com/lextudio/pysnmp):

```bash
$ pip install pysnmp
Collecting pysnmp
  Downloading pysnmp-7.1.16-py3-none-any.whl.metadata (4.3 kB)
Collecting pyasn1!=0.5.0,>=0.4.8 (from pysnmp)
  Downloading pyasn1-0.6.1-py3-none-any.whl.metadata (8.4 kB)
Downloading pysnmp-7.1.16-py3-none-any.whl (340 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 341.0/341.0 kB 1.4 MB/s eta 0:00:00
Downloading pyasn1-0.6.1-py3-none-any.whl (83 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 83.1/83.1 kB 2.4 MB/s eta 0:00:00
Installing collected packages: pyasn1, pysnmp
Successfully installed pyasn1-0.6.1 pysnmp-7.1.16
```

Paquets instal·lats:

```bash
$ pip freeze
pyasn1==0.6.1
pysnmp==7.1.16
```

## Primer test

A *v1-get.py* hi ha un primer script que fa un get sobre un dispositiu de demo. La sortida:

```bash
$ python3 v1-get.py 
SNMPv2-MIB::sysDescr.0 = #SNMP Agent on .NET Standard
```

## Com funciona PySNMP

### SNMP Engine

Qualsevol operació que es vulgui implementar amb aquest mòdul implica una instància de la classe `SnmpEngine`:

```python
snmpEngine = SnmpEngine()
```

Aconsellable cridar al final 

```python
snmpEngine.close_dispatcher()
```

### Queries

A *PySNMP* hi han les següents funcions que implementen consultes / operacions SNMP: 

```python
['bulk_cmd', 'bulk_walk_cmd', 'cmdgen', 'get_cmd', 'next_cmd', 'set_cmd', 'walk_cmd']
```

### SNMP protocol i credencials

Em centraré amb la versió 1 i la 2c, les quals accedeixen als agents a través de les cadenes de comunitat. Aquestes es declaren a partir de la classe `CommunityData`. El primer argument és el nom de la cadena i el segon és la versió de SNMP:

```python
CommunityData('public', mpModel=0)  # SNMPv1
CommunityData('public', mpModel=1)  # SNMPv2c
```

### Connexió amb agent

La connexió és per UDP fent servir la classe `UdpTransportTarget` i el seu mètode `create`. El primer argument és l'agent i el segon el port de l'agent:

```python
await UdpTransportTarget.create(("demo.pysnmp.com", 161))
```

### ContextData

Un agent pot gestionar múltiples col·leccions de MIBs representant diferents instàncies de Hw o Sw. `ContextData` serveix per especificar una en concret. Nosaltres la deixem amb els arguments per defecte, `ContextData()`.

### MIB Object

Per definir un OID i llur valor, necessitem dues classes: `ObjectIdentity` (OID) i `ObjectType` (OID i valor). `Objectype` tindrà el valor de l'OID retornat per l'agent:

```bash
>>> from pysnmp.hlapi.v3arch.asyncio import *
>>>
>>> g = await get_cmd(SnmpEngine(),
...            CommunityData('public'),
...            await UdpTransportTarget.create(('demo.pysnmp.com', 161)),
...            ContextData(),
...            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)))
>>> g
(None, 0, 0, [ObjectType(ObjectIdentity('1.3.6.1.2.1.1.3.0'), TimeTicks(44430646))])
```

Podem definir `ObjectIdentity` com a l'exemple o directament passant un string amb el valor de l'OID. Veure [MIB Variables](https://docs.lextudio.com/pysnmp/v7.1/docs/api-reference#mib-variables)