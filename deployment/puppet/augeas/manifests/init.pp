class augeas {
    file {  "augeas_nova":
        source => "puppet:///modules/augeas/nova.aug",
        path => "/usr/share/augeas/lenses/dist/nova.aug",
        recurse => true,
        mode => 0755
        }
     file {  "augeas_odc":
        source => "puppet:///modules/augeas/odc.aug",
        path => "/usr/share/augeas/lenses/dist/odc.aug",
        recurse => true,
        mode => 0755
        }
    }         
