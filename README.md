# moxie

A TCP proxy for OSX guaranteed to make you smile.

## What is it?

Moxie is a python script that helps manage SSH tunnels. In addition to creating the tunnel, it also tweaks your networking settings you can connect directly to the desired hostname (as if you didn't need a proxy in the first place!).

## How do I install it?

Clone the repo, make a virtualenv, run `pip install -r requirements.pip`

More robust info coming soon...

## How do I use it?

Let's say you need to proxy MySQL to db1.foo.com, db2.foo.com, and db.bar.com through blah.foo.com. Paste this into `~/.moxie.yaml`:

```yaml
routes:
  - destination: db1.foo.com
  - destination: db2.foo.com
  - destination: db.bar.com
defaults:
  - proxy: blah.foo.com
  - ports: [3306]
```

Then run `sudo moxie start`.

Check the status of your proxies with `moxie status`.

Finally, tear it all down with `sudo moxie stop`.

(better docs coming soon.)

## Theory of Operation

### SSH tunnels
A SSH tunnel allows you to proxy all traffic from a socket on a local machine to a socket on a remote machine by way of a 3rd party.

Let's say we wanted to connect to a MySQL databse on db.foo.com. Db.foo.com is behind a firewall, but test.foo.com is accessable. Here's a typical SSH command to proxy MySQL traffic to db.foo.com through test.foo.com:

`ssh -f tom@test.foo.com -L 3306:db.foo.com:3306 -N`

 - `-f` means run this command in the background
 - `tom@test.foo.com` means connect to test.foo.com as user "tom"
 - `-L 3306:db.foo.com:3306` means forward any local traffic on port 3306 to port 3306 on db.foo.com
 - `-N` means don't run any commands on test.foo.com (optional, but good for safety)

Now, if you connect to port 3306 on your own machine, the traffic will be proxied through test.foo.com to db.foo.com. Life is good.

But what if you had multiple firewalled database hosts you needed to connect to? Sure, you could tweak the script so that 3306 would proxy to the first database, 3307 would proxy to the next, etc..., but that's a pain in the ass. There is a better way.

### Multiple loopback addresses

On linux OSes, you can use the ifconfig command to gather information about your network interfaces:

```bash
new-host:~ tpetr$ ifconfig lo0
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
    options=3<RXCSUM,TXCSUM>
    inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1 
    inet 127.0.0.1 netmask 0xff000000 
    inet6 ::1 prefixlen 128
```

Did you know you can actually bind additional IP addresses to your loopback interface? In OSX, you can do so with the alias command:

```bash
new-host:~ tpetr$ sudo ifconfig lo0 alias 127.0.0.2
Password: **********
new-host:~ tpetr$ ifconfig lo0
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
    options=3<RXCSUM,TXCSUM>
    inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1 
    inet 127.0.0.1 netmask 0xff000000 
    inet6 ::1 prefixlen 128 
    inet 127.0.0.2 netmask 0xff000000
```

If we combine this with the fact that ssh's -L command allows you to specify a local address to listen on, we can use this to support multiple proxies listening on the same port:

```
ssh -f tom@test.foo.com -L 127.0.0.1:3306:db1.foo.com:3306 -N
ssh -f tom@test.foo.com -L 127.0.0.2:3306:db2.foo.com:3306 -N
```

Now, connecting to MySQL on 127.0.0.1 will proxy you to db1.foo.com, and connecting to MySQL on 127.0.0.2 will proxy you to db2.foo.com. Sweet.

There's one more thing we can do to make this SUPER convenient for is.

### Tieing it all together with /etc/hosts

The /etc/hosts file is a mapping of domains and IP addresses that gets checked **before** hitting DNS. Here's what a typical one looks like on OSX:

```
##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1   localhost
255.255.255.255 broadcasthost
::1             localhost 
fe80::1%lo0 localhost
```

If we map db1.foo.com to 127.0.0.1 and db2.foo.com to 127.0.0.2, does that mean we could connect to them as if they were never firewalled in the first place?

Yes, it does.

## Gotchas

Loopback address aliases and ssh tunnels won't survive reboots, but changes to /etc/hosts will.