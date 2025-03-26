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

## Pas 3. Configurem agent per a poder fer operacions snmpset

`snmpset` implementa la petició `SNMP SET` per modificar valors OID. Pots modificar més d'un OID en la mateixa petició. En la sintaxi has d'indicar l'OID, el tipus de valor i el nou valor de l'OID. Segons `man snmpset`:

```bash
SYNOPSIS
       snmpset [COMMON OPTIONS] AGENT OID TYPE VALUE [OID TYPE VALUE]...
```
```bash
       The TYPE is a single character, one of:
              i  INTEGER
              u  UNSIGNED
              s  STRING
              x  HEX STRING
              d  DECIMAL STRING
              n  NULLOBJ
              o  OBJID
              t  TIMETICKS
              a  IPADDRESS
              b  BITS
```

Si en el client tenim carregat l'esquema del MIB al que referenciem en el snmpset podem ficar el signe `=` en comptes del tipus.

Exemple. Vaig a canviar les dades de contacte de l'agent:

```bash
joan@super-ThinkBook-14-G4-IAP:~$ snmpset -v2c -c public 192.168.56.101 system.sysContact.0 s "Pedro Picapiedra <pedrowillma@gmail.com>"
Error in packet.
Reason: noAccess
Failed object: SNMPv2-MIB::sysContact.0
```

Vaja. No m'ha deixat. Això és perque la cadena de comunitat que estic fent servir (*public*) és de lectura només. Si vaig al fitxer de configuració de l'agent (`rocommunity  public  default -V allview`):

```bash
rocommunity  public  default -V allview
```

He de crear una altra cadena per lectura i escriptura:

```bash
rocommunity  public  default -V allview
rwcommunity  private  default -V allview
```

I reinicio l'agent:

```bash
profe@joshua:~$ systemctl restart snmpd.service 
==== AUTHENTICATING FOR org.freedesktop.systemd1.manage-units ====
Authentication is required to restart 'snmpd.service'.
Authenticating as: Juan Aguilera (profe)
Password: 
==== AUTHENTICATION COMPLETE ====
```

I torno a provar. Però em torna a donar un error, encara que lleugerament diferent:

```bash
joan@super-ThinkBook-14-G4-IAP:~$ snmpset -v2c -c private 192.168.56.101 system.sysContact.0 s "Pedro Picapiedra <pedrowillma@gmail.com>"
Error in packet.
Reason: notWritable (That object does not support modification)
Failed object: SNMPv2-MIB::sysContact.0
```

Ara no em diu que no tinc accés, sinó que l'objecte que vull modificar no és modificable (*notWritable*). Això és perquè en l'arxiu '/etc/snmp/snmpd.conf` tinc configurat el valor de sysContact amb un valor que no puc modificar. Si el vull modificar he de comentar la línea corresponent:

```bash
# syslocation: The [typically physical] location of the system.
#   Note that setting this value here means that when trying to
#   perform an snmp SET operation to the sysLocation.0 variable will make
#   the agent return the "notWritable" error code.  IE, including
#   this token in the snmpd.conf file will disable write access to
#   the variable.
#   arguments:  location_string
sysLocation    Sitting on the Dock of the Bay
# sysContact     Juan Aguilera <jaguilera126@gmail.com>

# sysservices: The proper value for the sysServices object.
#   arguments:  sysservices_number
sysServices    72
```

Reinicio i torno a provar:

```bash
joan@super-ThinkBook-14-G4-IAP:~$ snmpset -v2c -c private 192.168.56.101 system.sysContact.0 s "Pedro Picapiedra <pedrowillma@gmail.com>"
SNMPv2-MIB::sysContact.0 = STRING: Pedro Picapiedra <pedrowillma@gmail.com>
```