# Version --> 0.201

use Memory::Usage;
my $mu = Memory::Usage->new();
 
$mu->record('starting work');
 
$object->something_memory_intensive();
 
$mu->record('after something_memory_intensive()');
 
$mu->dump();
