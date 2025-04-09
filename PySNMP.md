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

## Funcions que farem servir en el projecte

### Com executar-les

Totes les funcions són assíncrones i per cridar-les ho podem fer així:

```python
# Exemple de crida de la funció snmpget

asyncio.run(snmpget(version, comm, agent, mib, oid))
```

### snmpget.py

La funció snmpget recull com a arguments la versió SNMP, la cadena de comunitat *rocommunity*, l'agent, el *MIB* (que crec que no ens farà falta) i l'*OID* llur valor volem consultar en l'agent.

retorna una llista de parells de valors (normalment aquesta llista serà d'un element). El primer valor de cada element és l'*OID* i el següent el valor associat que hi ha en l'agent.

#### Com fer-la servir

```python
    # Exemple de crida de snmpget i com fer servir la informació que retorna:

    # varBnds és una llsita per la qual iteraré
    varBinds = run_query(valor_query, valor_version, valor_rocomm, valor_agent, valor_mib, valor_oid, valor_set)

    # resultat és una llista i cada element de la llista és un diccionari que té dos claus, la clau oid i la clau value:
    resultat = [
            {"oid": str(varBind[0]), "value": varBind[1]} 
            for varBind in varBinds
        ]        
```

Després, la variable `resultat` (que és una llista) es pot passar a una plantilla amb la funció `render_template()` de Flask. Exemple de com fer-ne ús a la plantilla:

```python
    {% for varBind in resultat %}
        <p>
            oid: {{varBind["oid"]}} >>>> valor: {{varBind["value"]}}
        </p>
    {% endfor %}
```