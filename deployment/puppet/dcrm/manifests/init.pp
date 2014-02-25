class dcrm {
      
      notify { "Step 1":
        message => "Java 6 by IBM installation"
      }->
            
      file {  "/usr/lib/jvm/":
              ensure => "directory",
              owner => "root",
              group => "root",
              mode => 755
            }->
      
      file {  "java":
              source => "puppet:///modules/dcrm/ibm-java-jre-6.0-14.0-linux-x86_64.bin",
              path => "/usr/lib/jvm/java.bin",
              recurse => true,
              mode => 0755
            }->
      
      exec {  "/usr/lib/jvm/java.bin -i silent":
              path => "/usr/bin:/usr/sbin:/bin:/sbin",
              onlyif => "test -f /usr/lib/jvm/java.bin"
            }->
      
      exec {  "update-java-alternatives":
              path => "/usr/bin:/usr/sbin:/bin:/sbin",
              command => "update-alternatives --install /usr/bin/java java /usr/lib/jvm/ibm-java-x86_64-60/jre/bin/java 1", 
              onlyif => "test -f /usr/lib/jvm/ibm-java-x86_64-60/jre/bin/java"
            }->
      
      notify { "Step 2":
                message => "Pivot scheduler installation"
            }->
      
      /* Creation IBM directory */
      file {  "/opt/IBM/":
              ensure => "directory",
              owner => "root",
              group => "root",
              mode => 755
            }->
     
      file {  "pivot":
              source => "puppet:///modules/dcrm/pivot.tar.gz",
              path => "/opt/IBM/pivot.tar.gz",
              recurse => true,
              mode => 0755
            }->
     
      file {  "cplex":
              source => "puppet:///modules/dcrm/cplex.tar.gz",
              path => "/opt/IBM/cplex.tar.gz",
              recurse => true,
              mode => 0755
            }->
     
      exec {  "tar_pivot":
              command => "tar -xf /opt/IBM/pivot.tar.gz",
              cwd => "/opt/IBM",
              path => "/bin:/usr/bin"
            }->
     
      exec {  "tar_cplex":
              command => "tar -xf /opt/IBM/cplex.tar.gz",
              cwd => "/opt/IBM",
              path => "/bin:/usr/bin"
            }->
     
      file {  "/var/log/PIVOT/":
              ensure => "directory",
              owner => "root",
              group => "root",
              mode => 755
            }->
     
      file  { "log_pivot":
              target => "/var/log/PIVOT/",
              ensure => 'link',
              path => "/opt/IBM/PIVOT/logs"
            }->
    
      /* Backup nova,novaclient */
            
      notify { "Step 3":
                message => "Update nova and novaclient"
            }->
     
      exec {  "backup_nova":
              command => "tar -cf /usr/lib/python2.7/dist-packages/nova/nova.tar.gz /usr/lib/python2.7/dist-packages/nova/*",
              path => "/bin:/usr/bin",
              onlyif => "test -d /usr/lib/python2.7/dist-packages/nova"
            }->        
     
      exec {  "backup_novaclient":
              command => "tar -cf /usr/lib/python2.7/dist-packages/novaclient/novaclient.tar.gz /usr/lib/python2.7/dist-packages/novaclient/*",
              path => "/bin:/usr/bin",
              onlyif => "test -d /usr/lib/python2.7/dist-packages/novaclient"
            }->
      
      /* Extract nova, novaclient files */
      file {  "copy_nova":
              source => "puppet:///modules/dcrm/nova.tar.gz",
              path => "/tmp/nova.tar.gz",
              recurse => true,
              mode => 0777
            }->
      
      exec {  "untar_nova":
              command => "tar -xf /tmp/nova.tar.gz",
              cwd => "/tmp",
              path => "/bin:/usr/bin",
              onlyif => "test -f /tmp/nova.tar.gz"  
            }->	
      
      exec { "update_nova":
              command => "cp -R /tmp/nova/nova/* /usr/lib/python2.7/dist-packages/nova",
              path => "/usr/bin:/usr/sbin:/bin:/sbin"
            }->
      
      exec { "update_novaclient":
                command => "cp -R /tmp/nova/novaclient/* /usr/lib/python2.7/dist-packages/novaclient",
                path => "/usr/bin:/usr/sbin:/bin:/sbin"
            }
}         
