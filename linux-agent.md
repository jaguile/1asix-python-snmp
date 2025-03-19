# Preparem l'entorn de proves. Linux com a agent SNMP

# Linux as an agent

## Pas 1. Configurem el dimoni snmpd

He instal·lat el paquet `snmpd` en una màquina vuirtual Ubuntu Server 24.04 i he modificat algun paràmetre de la configuració per a que poguès escoltar peticions de la xarxa local.

![alt text](image-1.png)

![alt text](image-2.png)

He afegit a ferro la ip per la que vull que escolti l'agent. També puc afegir la línea 

```bash
agentaddress UDP:161
```

això farà que escolti per totes les interfícies en el port udp 161.

Després, vaig a afegir la següent línea per poder veure-ho tot en l'agent de cara a poder fer proves:

```bash
###########################################################################
# SECTION: Access Control Setup
#
#   This section defines who is allowed to talk to your running
#   snmp agent.

# Views 
#   arguments viewname included [oid]

#  system + hrSystem groups only
view   allview    included   .1
```

i reemplacem la directiva `rocommunity` per 

```bash
rocommunity  public  default -V allview
```

Vaig a fer proves de moment amb SNMPv1 i SNMPv2c en mode només lectura:

![alt text](image-3.png)

Finalment, fem un `$ sudo systemctl restart snmpd.service`.

![alt text](image-4.png)

## Pas 2. Instal·lem i configurem el client

```bash
$ sudo apt install snmp
```

Aquest paquet et permet de fer consultes a un agent. Si volem treballar amb noms i no directament amb OID, hem d'instal·lar també els MiB en el client, de cara a poder tenir l'estructura de la base de dades i els noms simbòlics dels objectes (OID) de la taula:

```bash
$ sudo apt install snmp-mibs-downloader
```

I comentar també la directiva `mibs` a `/etc/snmp/snmp.conf`:

```bash
# mibs: 
```