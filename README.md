# moxie: A TCP proxy guaranteed to make you smile.

v0.3

## What is it?

Moxie is a python script that helps manage SSH tunnels. It also fiddles with networking settings to make the tunnel(s) appear transparent to the end user.

## How do I install it?

Clone this repository and then run `./install.sh`.

We will be publishing moxie to the public PyPI soon.

## How do I use it?

Run `moxie status` to check the status of your tunnels:

```
(moxie)Macintosh:moxie tpetr$ moxie status
No routes configured.

Add one via the "moxie add" command or by editing ~/.moxie.yaml
```

Let's use moxie to proxy all MySQL traffic to db1.foo.com through another host:

```
(moxie)Macintosh:moxie tpetr$ moxie add db1.foo.com 3306
No default proxy set.

Include a --proxy argument, or set a default proxy in your moxie config.
```

D'oh, we forgot to set a default proxy. Let's set some defaults in our `~/.moxie.yaml` file:

```
(moxie)Macintosh:moxie tpetr$ cat <<EOF > ~/.moxie.yaml
> defaults:
>     proxy: tpetr@myhost.foo.com
>     ports: [3306]
> EOF
(moxie)Macintosh:moxie tpetr$ moxie add db1.foo.com 3306
Added route. Run "moxie start" to start proxying.
(moxie)Macintosh:moxie tpetr$ moxie status
db1.foo.com:3306 OFF
```

Proxying is an art -- let us paint.

```
(moxie)Macintosh:moxie tpetr$ sudo moxie start
Password: ********
INFO:root:Proxying db1.foo.com:3306 through tpetr@myhost.foo.com
(moxie)Macintosh:moxie tpetr$ moxie status
db1.foo.com:3306 OK
```

Tearing down the proxies is as simple as a `moxie stop`:

```
(moxie)Macintosh:moxie tpetr$ sudo moxie stop
Password: ********
INFO:root:Stopped proxying db1.foo.com:3306 through tpetr@myhost.foo.com
```

## Theory of Operation

### SSH tunnels
A SSH tunnel allows you to proxy all traffic from a socket on a local machine to a socket on a remote machine by way of a 3rd party.

Let's say we wanted to connect to a MySQL databse on db.foo.com. Db.foo.com is behind a firewall, but test.foo.com is accessable. Here's a typical SSH command to proxy MySQL traffic to db.foo.com through test.foo.com:

`ssh -f tom@test.foo.com -L 3306:db.foo.com:3306 -N`

 - `-f` means run this command in the background
 - `tom@test.foo.com` means connect to test.foo.com as user "tom"
 - `-L 3306:db.foo.com:3306` means forward any local traffic on port 3306 to port 3306 on db.foo.com
 - `-N` means don't run any commands on test.foo.com (optional, but encouraged for Good, Clean Living&trade;)

Now, if you connect to port 3306 on your own machine, the traffic will be proxied through test.foo.com to db.foo.com. Life is good.

But what if you had multiple firewalled database hosts you needed to connect to? Sure, you could tweak the script so that 3306 would proxy to the first database, 3307 would proxy to the next, etc..., but that's a pain in the ass.

There is a better way.

### Multiple loopback addresses

**Note:** This information is specific to OSX. Most other UNIXy operating systems map 127.*.*.* to the loopback interface, rendering this step moot.

In OSX, you can use the `ifconfig` command to gather information about your network interfaces:

```
new-host:~ tpetr$ ifconfig lo0
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
    options=3<RXCSUM,TXCSUM>
    inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1 
    inet 127.0.0.1 netmask 0xff000000 
    inet6 ::1 prefixlen 128
```

Did you know you can actually bind additional IP addresses to an interface via the `alias` command?

```
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

If we combine this with the fact that ssh's -L command allows you to additionally specify a address to listen on, we can use this to support multiple tunnels listening on the same port:

```
ssh -f tom@test.foo.com -L 127.0.0.1:3306:db1.foo.com:3306 -N
ssh -f tom@test.foo.com -L 127.0.0.2:3306:db2.foo.com:3306 -N
```

Now, connecting to MySQL on 127.0.0.1 will proxy you to db1.foo.com, and connecting to MySQL on 127.0.0.2 will proxy you to db2.foo.com. Sweet.

### Tieing it all together with /etc/hosts

The `/etc/hosts` file is a mapping of domains and IP addresses that gets checked **before** hitting DNS. Here's what a typical one looks like on OSX:

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

If we map db1.foo.com to 127.0.0.1 and db2.foo.com to 127.0.0.2, does that mean we could connect to them as if they were never firewalled in the first place? Yes, it does.

This is moxie in a nutshell.

## Any gotchas?

 - SSH tunnels won't survive reboots, but local addresses and `/etc/hosts` tweaks will

## I'd like to help out.

Thanks! Please send all pull requests to [@tpetr](https://github.com/tpetr/) (tpetr@hubspot.com).

## Tested on

 - OSX 10.7.5
 - Ubuntu 12.10

## License

The code is licensed under the MIT license.