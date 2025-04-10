/* REXX ***************************************************************
* - Retrieve all member names from a PDS: PROD001.TENNIS              *
* - Retrieve the content of the first member                          *
**********************************************************************/
pds = 'PROD001.TENNIS'

x = outtrap(list.)
"listds '"pds"' members"
x = outtrap(off)
say pds; say copies('-',25)
start='no'
cont = 0
do i = 0 to list.0
   list.i=strip(list.i)
   if start = 'yes' then do
      cont=cont+1
      members.cont=list.i
      say members.cont
   end
   if list.i = '--MEMBERS--' then start='yes'
end
members.0=cont

"alloc da('"pds"("members.1")') fi(mydd) shr reu"
"execio * diskr mydd (finis stem frstmem."; "free fi(mydd)"
say ''; say pds"("members.1")"; say copies('-',25)
do i = 1 to frstmem.0
   say frstmem.i
end
exit
