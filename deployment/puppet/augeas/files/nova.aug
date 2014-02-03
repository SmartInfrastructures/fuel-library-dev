(* Nova Openstack for Augeas                     *)
(* Author: alessandro.martellone@create-net.org  *)

module NOVA =
  autoload xfm

(************************************************************************
 * INI File settings
 *************************************************************************)

let comment  = IniFile.comment IniFile.comment_re IniFile.comment_default
let sep      = IniFile.sep IniFile.sep_re IniFile.sep_default
let empty    = IniFile.empty

let entry    = IniFile.indented_entry IniFile.entry_re sep comment


(************************************************************************
 *                         TITLE
 *
 * We use IniFile.title_label because there can be entries
 * outside of sections whose labels would conflict with section names
 *************************************************************************)
let title       = IniFile.title ( IniFile.record_re - ".nova" )
let record      = IniFile.record title entry

let record_nova = [ label ".nova" . ( entry | empty )+ ]


(************************************************************************
 *                         LENS & FILTER
 * There can be entries before any section
 * IniFile.entry includes comment management, so we just pass entry to lns
 *************************************************************************)
let lns    = record_nova? . record*

let filter = (incl "/etc/nova/nova*.conf")
             . Util.stdexcl

let xfm = transform lns filter