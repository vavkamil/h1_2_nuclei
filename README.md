# h1_2_nuclei

Scan any HackerOne program with Nuclei

## Usage

```
$ python3 h1_2_nuclei.py -h
                       _            _                       
 |_|  _.  _ |   _  ._ / \ ._   _     )   |\ |      _ |  _  o
 | | (_| (_ |< (/_ |  \_/ | | (/_   /_   | \| |_| (_ | (/_ |

usage: h1_2_nuclei.py [-h] -handle HANDLE

xx

optional arguments:
  -h, --help      show this help message and exit
  -handle HANDLE  Private program handle

Have a nice day :)
```

## Example

```
$ python3 h1_2_nuclei.py -handle security
                       _            _                       
 |_|  _.  _ |   _  ._ / \ ._   _     )   |\ |      _ |  _  o
 | | (_| (_ |< (/_ |  \_/ | | (/_   /_   | \| |_| (_ | (/_ |

[i] Checking scope for: security
[i] Parsing scope items

[i] Wildcards in scope:	 1
[i] Hosts in scope:	 8
[i] Hosts out of scope:	 5

[i] Checking subdomains with chaos

[i] Hosts in scope:	 9
[i] Hosts out of scope:	 5

[i] Removing out of scope items

[i] Unique hosts in scope: 9

[i] Saving hosts to: targets/security/chaos_security_21-08-24.txt

[i] Resolving subdomains with httpx
[i] Output saved to: targets/security/httpx_security_21-08-24.txt

[i] Number of live targets: 6

[i] Scanning targets with Nuclei
[i] Output saved to: targets/security/nuclei_security_21-08-24.txt

[i] Vulnerabilities found: 0
```
