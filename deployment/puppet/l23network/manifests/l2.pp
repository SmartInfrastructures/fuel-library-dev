# == Class: l23network::l2
#
# Module for configuring L2 network.
# Requirements, packages and services.
#
class l23network::l2 (
  $use_ovs          = true,
  $use_lnx          = true,
  $install_ovs      = $use_ovs,
  $install_brtool   = $use_lnx,
  $install_ethtool  = $use_lnx,
  $install_bondtool = $use_lnx,
  $install_vlantool = $use_lnx,
  $ovs_modname      = 'openvswitch'
){
  include stdlib
  include ::l23network::params

  if $use_ovs {
    $ovs_mod_ensure = present
    if $install_ovs {
      if $::l23network::params::ovs_datapath_package_name {
        package { 'openvswitch-datapath':
          name => $::l23network::params::ovs_datapath_package_name
        }
      }
      package { 'openvswitch-common':
        name => $::l23network::params::ovs_common_package_name
      }

      Package<| title=='openvswitch-datapath' |> -> Package['openvswitch-common']
      Package['openvswitch-common'] ~> Service['openvswitch-service']
    }
    $ovs_service_ensure = 'running'
  } else {
    $ovs_mod_ensure = absent
    $ovs_service_ensure = 'stopped'
  }
  service {'openvswitch-service':
    ensure    => $ovs_service_ensure,
    name      => $::l23network::params::ovs_service_name,
    enable    => $ovs_service_ensure == 'running',
    hasstatus => true,
  }
  Service['openvswitch-service'] -> Anchor['l23network::l2::init']

  @k_mod{$ovs_modname:
    ensure => $ovs_mod_ensure
  }

  if $use_lnx {
    $mod_8021q_ensure = present
    $mod_bonding_ensure = present
    $mod_bridge_ensure = present
  } else {
    $mod_8021q_ensure = absent
    $mod_bonding_ensure = absent
    $mod_bridge_ensure = absent
  }

  if $install_vlantool and $::l23network::params::lnx_vlan_tools {
    ensure_packages($::l23network::params::lnx_vlan_tools)
    Package[$::l23network::params::lnx_vlan_tools] -> Anchor['l23network::l2::init']
  }
  @k_mod{'8021q':
    ensure => $mod_8021q_ensure
  }

  if $install_bondtool and $::l23network::params::lnx_bond_tools {
    ensure_packages($::l23network::params::lnx_bond_tools)
    Package[$::l23network::params::lnx_bond_tools] -> Anchor['l23network::l2::init']
  }
  @k_mod{'bonding':
    ensure => $mod_bonding_ensure
  }

  if $install_brtool and $::l23network::params::lnx_bridge_tools {
    ensure_packages($::l23network::params::lnx_bridge_tools)
    #Package[$::l23network::params::lnx_bridge_tools] -> Anchor['l23network::l2::init']
  }
  @k_mod{'bridge':
    ensure => $mod_bridge_ensure
  }

  if $install_ethtool and $::l23network::params::lnx_ethernet_tools {
    ensure_packages($::l23network::params::lnx_ethernet_tools)
    Package[$::l23network::params::lnx_ethernet_tools] -> Anchor['l23network::l2::init']
  }

  anchor { 'l23network::l2::init': }

}
