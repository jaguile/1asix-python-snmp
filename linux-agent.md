# Preparem l'entorn de proves. Linux com a agent SNMP

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

## Pas 4. Configurar l'agent i el NM per a l'enviament de traps

Els *TRAPS* a **SNMP** són notificacions des de l'agent cap al *SNMP manager*. A Linux, podem rebre TRAPS d'agents amb el dimoni *snmptrapd* instal·lat al *SNMP Manager*. 

A un agent Linux podem enviar *TRAPS* amb la comanda `snmptrap`. La sintaxi de la comanda depèn molt de la versió de *SNMP*, però bàsicament, hem d'especificar la versió, la cadena de comunitat del *Network Manager*, l'adreça del *Network Manager*, un OID de tipus trap (OID_trap) i un o més OIDs amb valors.

Hi han dues categories de traps:

1. Genèrics

2. Específics, creats per empreses

Els OID de traps genèrics són els següents:

```bash
joan@super-ThinkBook-14-G4-IAP:~$ snmptranslate -Tp .1.3.6.1.6.3.1.1.5
+--snmpTraps(5)
   |
   +--coldStart(1)
   +--warmStart(2)
   +--linkDown(3)
   +--linkUp(4)
   +--authenticationFailure(5)
```

Anem a fer la primera prova. Primer, haurem de configurar el *SNMP Manager* per a que pugui escoltar possibles notificacion:

```bash
joan@super-ThinkBook-14-G4-IAP:~$ apt search snmptrap
S'està ordenant… Fet
Cerca a tot el text… Fet
libnetsnmptrapd40t64/noble 5.9.4+dfsg-1.1ubuntu3 amd64
  SNMP (Simple Network Management Protocol) trap library

snmptrapd/noble 5.9.4+dfsg-1.1ubuntu3 amd64
  Net-SNMP notification receiver

snmptrapfmt/noble 1.18 amd64
  configurable snmp trap handler daemon for snmpd

snmptt/noble,noble 1.5-1 all
  SNMP trap handler for use with snmptrapd
```

D'aquests paquets, m'interessa instal·lar el paquet `snmptrapd`.

De quina manera puc processar els traps a snmptrapd? `man snmptrapd.conf`:

```bash
There are currently three types of processing that can be specified:

              log    log  the  details of the notification - either in a specified file,
                     to standard output (or stderr), or via syslog (or similar).

              execute
                     pass the details of the trap to a specified  handler  program,  in‐
                     cluding embedded perl.

              net    forward the trap to another notification receiver.
```

Descomento / afegeixo aquestes línees en el fitxer de configuració `/etc/snmp/snmptrapd.conf` (*SNMP Manager*):

```bash
disableAuthorization yes
authCommunity log,execute,net public
snmpTrapdAddr udp:162
```

Fem un restart del servei i ja tenim actiu el port 162 per escoltar traps:

```bash
joan@super-ThinkBook-14-G4-IAP:~$ sudo netstat -ul | grep snmp
udp        0      0 localhost:snmp          0.0.0.0:*                          
udp        0      0 0.0.0.0:snmp-trap       0.0.0.0:*                          
udp6       0      0 ip6-localhost:snmp      [::]:*                             
udp6       0      0 [::]:snmp-trap          [::]:*                             
```

Exemple de *TRAP* enviat des de client amb la comanda `snmptrap`:

```bash
profe@joshua:~$ snmptrap -v2c -c public 192.168.56.1 '' SNMPv2-MIB::coldStart.0 SNMPv2-MIB::sysName.0 s "MyDevice"
```

Aquesta comanda envia un trap amb la versió 2c a la cadena de comunitat *public* i al *SNMP Manager* 192.168.56.1. És un *TRAP* de tipus `coldStart` i EL *TRAP* passa el `sysName` amb valor *MyDevice*. A part dels OIDs amb llurs valors que afegim al trap i del OID_type, també s'envia per defecte l'OID `sysUpTime`:

![alt text](image-5.png)

**Exemple de com gestionar els traps rebuts**

Anem a fer que els traps rebuts s'escriguin el fitxer de log `/var/log/trap.log`. Per això, he fet l'script en bash `snmptrap2log.sh:

```bash
#!/bin/bash
# Escric els traps a un fitxer de logs
LOG_F=/var/log/trap.log

DATA=$(date +"%Y-%m-%d %T")

while read line; do
	echo "Capturat trap -- $DATA -- " >> $LOG_F
	echo "----------------------------------" >> $LOG_F
	echo "$line" >> $LOG_F
	echo "----------------------------------" >> $LOG_F
	echo >> $LOG_F
done
```

Per a que aquest script pugui procesar el *TRAP* he d'afegir també la següent línea al `snmptrapd.conf`:

```bash
traphandle default /usr/bin/snmptrap2log.sh
```

Quan executo des de l'agent el *TRAP* d'abans, obtinc:

```bash
Capturat trap -- 2025-02-28 10:06:23 -- 
----------------------------------
<UNKNOWN>
UDP: [192.168.56.101]:56365->[192.168.56.1]:162
SNMPv2-MIB::snmpTrapOID.0 SNMPv2-MIB::coldStart.0
SNMPv2-MIB::sysName.0 MyDevice
----------------------------------
```

## Pas 5. Exemple de com gestionar i inserir els traps en una base de dades

Per comoditat, vaig a instal·lar *Mariadb* en l'agent (que és una màquina virtual). El lògic seria tenir la base de dades en un servidor centralitzant tots els traps que ens arribessin de tots els agents de la xarxa. 

He de configurar el servei per a que escolti peticions a la xarxa (no només a localhost) i crearé un usuari a Mariadb, *mib*, que tingui accés a la base de dades *mib_browser*.

**Pas 5.0. Instal·lo *Mariadb***

**Pas 5.1. Password de l'usuari root a *Mariadb***
Un cop instal·lo el servei, executo `$ sudo mysql_secure_installation` per establir l'usuari de root.

**Pas 5.2. Faig que escolti peticions a la xarxa**
He de comentar el paràmetre `bind-address` o donar-li el valor `0.0.0.0` editant l'arxiu `/etc/mysql/mariadb.conf.d/50-server.cnf`

**Pas 5.3. Creació de la base de dades i de l'usuari que accedirà a la base de dades per afegir els traps**
 
En aquest pas segueixo els passos de la variant 1 del següent enllaç:

[snmptrap collector](https://github.com/n0braist/snmp_trap_collector)

Que, bàsicament, és, crear la base de dades *net_snmp* amb un parell de taules:

```bash
$ mysql -u root -p
USE net_snmp;
DROP TABLE IF EXISTS notifications;
CREATE TABLE IF NOT EXISTS `notifications` (
  `trap_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `date_time` datetime NOT NULL,
  `host` varchar(255) NOT NULL,
  `auth` varchar(255) NOT NULL,
  `type` ENUM('get','getnext','response','set','trap','getbulk','inform','trap2','report') NOT NULL,
  `version` ENUM('v1','v2c', 'unsupported(v2u)','v3') NOT NULL,
  `request_id` int(11) unsigned NOT NULL,
  `snmpTrapOID` varchar(1024) NOT NULL,
  `transport` varchar(255) NOT NULL,
  `security_model` ENUM('snmpV1','snmpV2c','USM') NOT NULL,
  `v3msgid` int(11) unsigned,
  `v3security_level` ENUM('noAuthNoPriv','authNoPriv','authPriv'),
  `v3context_name` varchar(32),
  `v3context_engine` varchar(64),
  `v3security_name` varchar(32),
  `v3security_engine` varchar(64),
  PRIMARY KEY  (`trap_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS varbinds;
CREATE TABLE IF NOT EXISTS `varbinds` (
  `trap_id` int(11) unsigned NOT NULL default '0',
  `oid` varchar(1024) NOT NULL,
  `type` ENUM('boolean','integer','bit','octet','null','oid','ipaddress','counter','unsigned','timeticks','opaque','unused1','counter64','unused2') NOT NULL,
  `value` blob NOT NULL,
  KEY `trap_id` (`trap_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
```

La creació de l'usuari i permisos per accedir-hi a la base de dades que acabem de generar: 

```bash
MariaDB [(none)]> create user mib identified by "password";
MariaDB [(none)]> grant all privileges on net_snmp.* to mib;
```

Allà on tingui el dimoni *snmptrapd*, afegeixo aquestes dues línees a `/etc/snmp/snmptrapd.conf`:

```bash
# Logs a base de dades
sqlMaxQueue 1
sqlSaveInterval 9
```

I, allà on tingui la base de dades, genero fitxer a `/etc/mysql/conf.d/snmptrapd.cnf` amb les credencials per connectar-me a la base de dades que tinc a l'agent:

```bash
[snmptrapd]
user=mib
password=password
host=192.168.56.101
```

I ja està. Un cop reiniciat el `snmptrapd` ja podem capturar traps dels agents.

Per exemple, si jo envio des de l'agent:

```bash
$ snmptrap -v2c -c public 192.168.56.1 192.168.56.101 SNMPv2-MIB::coldStart.0 SNMPv2-MIB::sysName.0 s "MyDevice"
```

A la base de dades, tinc:

```bash
MariaDB [net_snmp]> select * from varbinds;
+---------+------------------------+-------+-----------------------------+
| trap_id | oid                    | type  | value                       |
+---------+------------------------+-------+-----------------------------+
|       1 | .1.3.6.1.6.3.1.1.4.1.0 | oid   | OID: .1.3.6.1.6.3.1.1.5.1.0 |
|       1 | .1.3.6.1.2.1.1.5.0     | octet | STRING: "MyDevice"          |
+---------+------------------------+-------+-----------------------------+
2 rows in set (0,000 sec)
```