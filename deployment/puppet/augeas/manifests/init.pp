class augeas {
    file {  "augeas_nova":
        source => "puppet:///modules/augeas/nova.aug",
        path => "/usr/share/augeas/lenses/dist/nova.aug",
        recurse => true,
        mode => 0755
        }
    }         