## This is class installed nagios master
# ==Parameters
## proj_name       => isolated configuration for project
## templatehost    => checks,intervals parameters for hosts (as Hash)
# name - name of this template
# check_interval check command interval for hosts included in this group
#
## templateservice => checks,intervals parameters for services (as Hash)
# name - name of this template
# check_interval check command interval for services included in this group
#
## hostgroups      =>  create hostgroups
# Put all hostgroups from nrpe here (as Array)
class nagios::master (
$proj_name         = 'conf.d',
$nginx            = false,
$hostgroups        = [],
$templatehost      = {'name' => 'default-host','check_interval' => '60'},
$templateservice   = {'name' => 'default-service' ,'check_interval'=>'60'},
$htpasswd          = {'nagiosadmin' => 'nagiosadmin'},
$contactgroups     = {'group' => 'admins', 'alias' => 'Admins'},
$contacts          = {'user' => 'hotkey', 'alias' => 'Dennis Hoppe',
                      'email' => 'nagios@%{domain}',
                      'group' => 'admins'},
$rabbitmq          = false,
$mysql_user        = 'root',
$mysql_pass        = 'nova',
$rabbit_user       = 'nova',
$rabbit_pass       = 'nova',
$rabbit_port       = '5672',
$mysql_port        = '3306',
$nagios3pkg        = $nagios::params::nagios3pkg,
$masterservice     = $nagios::params::nagios_os_name,
$masterdir         = $nagios::params::nagios_os_name,
$htpasswd_file     = $nagios::params::htpasswd_file,
) inherits nagios::params {

  notify { "***** Beginning deployment of nagios master on host ${::hostname} *****": }

  $master_proj_name = "${proj_name}_master"

  validate_hash($htpasswd)
  validate_hash($templateservice)
  validate_hash($templatehost)
  validate_hash($contactgroups)
  validate_hash($contacts)

  if $nginx == true {
    include nagios::nginx
  }

  include nagios::host
  include nagios::service
  include nagios::command
  include nagios::contact

  if $::osfamily == 'Debian' {
    exec { 'external-commands':
      command => 'dpkg-statoverride --update --add nagios nagios 751 /var/lib/nagios3 && dpkg-statoverride --update --add nagios www-data 2710 /var/lib/nagios3/rw',
      path    => ['/bin','/sbin','/usr/sbin/','/usr/sbin/'],
      unless  => 'dpkg-statoverride --list nagios nagios 751 /var/lib/nagios3 && dpkg-statoverride --list nagios www-data 2710 /var/lib/nagios3/rw',
    }
    #temp - we will fix the iso ;)
  }

  # Bug: 3299
    exec { 'fix-permissions':
      # FIXME: Giving the read permission to others seems a bit too open...
      #        Why not do a chown on the files?
      command     => "chmod -R go+r /etc/${masterdir}/${master_proj_name}",
      path        => ['/bin','/sbin','/usr/sbin/','/usr/sbin/'],
      refreshonly => true,
    }

  package {$nagios3pkg:}

  if  $::osfamily == 'RedHat' and $rabbitmq == true {
    package {'nagios-plugins-os-rabbitmq':
      require => Package[$nagios3pkg]
    }
  }

  case $::osfamily {
    'RedHat': {
      augeas {'configs':
        lens    => 'NagiosCfg.lns',
        incl    => '/etc/nagios*/*.cfg',
        context => "/files/etc/${masterdir}/nagios.cfg",
        changes => [
          'rm cfg_file[position() > 1]',
          "set cfg_dir \"/etc/${masterdir}/${master_proj_name}\"",
          'set check_external_commands 1',
        ],
        require => Package[$nagios3pkg],
      }
    }
    'Debian': {
      augeas {'configs':
        lens    => 'NagiosCfg.lns',
        incl    => '/etc/nagios*/*.cfg',
        context => "/files/etc/${masterdir}/nagios.cfg",
        changes => [
          "set cfg_dir[2] \"/etc/${masterdir}/${master_proj_name}\"",
          'set check_external_commands 1',
        ],
        require => Package[$nagios3pkg],
      }
    }
  }

  File {
      owner   => root,
      group   => nagios,
      mode    => '0644',
      require => Package[$nagios3pkg],
  }
  file { "base_dir_install_nagios":
    path => "/var/tmp/nagios-install/",
    ensure => "directory",
    owner  => "root",
    group  => "root",
    recurse => "true",
    mode   => "0750",
    require => Package[$nagios3pkg],
  }

  file { "dir_install_nagios":
    path => "/var/tmp/nagios-install/packages",
    ensure => "directory",
    owner  => "root",
    group  => "root",
    recurse => "true",
    mode   => "0750",
    source => "puppet:///modules/nagios/packages/",
    require => File["base_dir_install_nagios"],
  }

  file { "script_install_nagios":
    source => "puppet:///modules/nagios/install_nagios-3.5.1",
    path => "/var/tmp/nagios-install/install_nagios-3.5.1",
    mode => 0700,
    require => File["dir_install_nagios"],
  }

  exec { "exec_install_nagios":
    path => "/usr/bin:/usr/sbin:/bin:/sbin",
    cwd => "/var/tmp/nagios-install",
    command => "/var/tmp/nagios-install/install_nagios-3.5.1",
    onlyif => '/usr/bin/test ! -e /etc/nagios3/nagios-3.5.1.flag',
    require => File["script_install_nagios"],
  }

  file {
    "/etc/${masterdir}/${master_proj_name}/templates.cfg":
      content => template('nagios/openstack/templates.cfg.erb');
    "/etc/${masterdir}/${htpasswd_file}":
      content => template('nagios/common/etc/nagios3/htpasswd.users.erb');
  }

  file { "/etc/${masterdir}/${master_proj_name}":
    recurse => true,
    source  => 'puppet:///modules/nagios/common/etc/nagios3/conf.d',
  }

  Resources {
    purge => true,
  }

  resources {
    'nagios_command':;
    'nagios_contact':;
    'nagios_contactgroup':;
    'nagios_host':;
    'nagios_hostgroup':;
    'nagios_hostextinfo':;
    'nagios_service':;
    'nagios_servicegroup':;
  }

  #TODO remove fix_and_run script in order to fix glance-registry service bug
  file { "script_copy_fix":
    source => "puppet:///modules/nagios/fix_and_run.sh",
    path => "/etc/${masterdir}/${master_proj_name}/fix_and_run.sh",
    recurse => true,
    mode => 0755,
    require => Exec["exec_install_nagios"],
  }

  $deployment_id = $::fuel_settings['deployment_id']

  $tag = "deployment_${deployment_id}"

  notify{ "**** importing host with tag ${tag} *****": }

  Nagios_host <<|tag==$tag|>> {
    notify  => Exec['fix-permissions'],
    require => File["/etc/${masterdir}/${master_proj_name}"],
  }->
  exec { "script_fix_and_run":
    path => "/usr/bin:/usr/sbin:/bin:/sbin",
    command => "sh /etc/${masterdir}/${master_proj_name}/fix_and_run.sh",
    onlyif => "test -f /etc/${masterdir}/${master_proj_name}/fix_and_run.sh",
  }

  cron { puppet-agent:
    command => "puppet agent --onetime --tags=nagios",
    user    => root,
    minute  => '*/10'
  }

}
