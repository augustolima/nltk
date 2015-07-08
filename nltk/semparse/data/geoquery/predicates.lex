# WORDS
50 :: \x.(EQUAL(x, 50))
50 :: \P x.(COUNT(x, 50) & P(x))
Alabama :: \x.(EQUAL(x, alabama))
Alaska :: \x.(EQUAL(x, alaska))
Albany :: \x.(EQUAL(x, albany))
America :: \x.(EQUAL(x, america))
American :: \P x.(P(american(x)) & P(x))
Antonio :: \x.(EQUAL(x, antonio))
Arizona :: \x.(EQUAL(x, arizona))
Arkansas :: \x.(EQUAL(x, arkansas))
Atlanta :: \x.(EQUAL(x, atlanta))
Austin :: \x.(EQUAL(x, austin))
Baton :: \x.(EQUAL(x, baton))
Boston :: \x.(EQUAL(x, boston))
Boulder :: \x.(EQUAL(x, boulder))
California :: \x.(EQUAL(x, california))
Carolina :: \x.(EQUAL(x, carolina))
Chattahoochee :: \x.(EQUAL(x, chattahoochee))
Chicago :: \x.(EQUAL(x, chicago))
City :: \x.(EQUAL(x, city))
Colorado :: \x.(EQUAL(x, colorado))
Columbus :: \x.(columbus(x))
Count :: \x.(EQUAL(x, count))
DC :: \x.(EQUAL(x, dc))
Dakota :: \x.(EQUAL(x, dakota))
Dallas :: \x.(EQUAL(x, dallas))
Death :: \x.(EQUAL(x, death))
Delaware :: \x.(EQUAL(x, delaware))
Denver :: \x.(EQUAL(x, denver))
Des :: \x.(des(x))
Des :: \x.(EQUAL(x, des))
Detroit :: \x.(EQUAL(x, detroit))
Diego :: \x.(EQUAL(x, diego))
Dover :: \x.(EQUAL(x, dover))
Durham :: \x.(EQUAL(x, durham))
Erie :: \x.(EQUAL(x, erie))
Flint :: \x.(flint(x))
Florida :: \x.(EQUAL(x, florida))
Fort :: \x.(EQUAL(x, fort))
Francisco :: \x.(EQUAL(x, francisco))
GA :: \x.(EQUAL(x, ga))
Georgia :: \x.(EQUAL(x, georgia))
Give :: \B C e. exists y z .(give:1(e, y) & give:2(e, z) & C(y) & B(z))
Give :: \B C D e. exists y z w .(give:1(e, y) & give:2(e, z) & give:3(e, w) & D(y) & C(z) & B(w))
Grande :: \x.(EQUAL(x, grande))
Guadalupe :: \x.(EQUAL(x, guadalupe))
Hampshire :: \x.(EQUAL(x, hampshire))
Hawaii :: \x.(EQUAL(x, hawaii))
Houston :: \x.(EQUAL(x, houston))
How :: \P. exists x.(TARGET(x) & P(x))
How :: \P Q x. exists e.(P(x,e) & Q(x))
Idaho :: \x.(EQUAL(x, idaho))
Illinois :: \x.(EQUAL(x, illinois))
In :: \B C y e. exists z .(C(in:1(e, y)) & C(in:2(e, z)) & C(y) & B(z))
Indiana :: \x.(EQUAL(x, indiana))
Indianapolis :: \x.(EQUAL(x, indianapolis))
Iowa :: \x.(EQUAL(x, iowa))
Island :: \x.(EQUAL(x, island))
Jersey :: \x.(EQUAL(x, jersey))
Jose :: \x.(EQUAL(x, jose))
Kalamazoo :: \x.(EQUAL(x, kalamazoo))
Kansas :: \x.(EQUAL(x, kansas))
Kentucky :: \x.(EQUAL(x, kentucky))
Lake :: \x.(EQUAL(x, lake))
List :: \B C e. exists y z .(list:1(e, y) & list:2(e, z) & C(y) & B(z))
Louisiana :: \x.(EQUAL(x, louisiana))
Maine :: \x.(EQUAL(x, maine))
Maryland :: \x.(EQUAL(x, maryland))
Massachusetts :: \x.(EQUAL(x, massachusetts))
McKinley :: \x.(EQUAL(x, mckinley))
Mexico :: \x.(EQUAL(x, mexico))
Miami :: \x.(EQUAL(x, miami))
Michigan :: \x.(EQUAL(x, michigan))
Minneapolis :: \x.(EQUAL(x, minneapolis))
Minnesota :: \x.(EQUAL(x, minnesota))
Mississippi :: \x.(EQUAL(x, mississippi))
Missouri :: \x.(EQUAL(x, missouri))
Moines :: \x.(EQUAL(x, moines))
Montana :: \x.(EQUAL(x, montana))
Montgomery :: \x.(EQUAL(x, montgomery))
Mount :: \x.(EQUAL(x, mount))
Name :: \B C e. exists y z .(name:1(e, y) & name:2(e, z) & C(y) & B(z))
Name :: \x.(EQUAL(x, name))
Nebraska :: \x.(EQUAL(x, nebraska))
Nevada :: \x.(EQUAL(x, nevada))
New :: \x.(EQUAL(x, new))
North :: \x.(EQUAL(x, north))
Number :: \x.(EQUAL(x, number))
Of :: \B C y e. exists z .(C(of:1(e, y)) & C(of:2(e, z)) & C(y) & B(z))
Ohio :: \x.(EQUAL(x, ohio))
Oklahoma :: \x.(EQUAL(x, oklahoma))
Oregon :: \x.(EQUAL(x, oregon))
Orleans :: \x.(EQUAL(x, orleans))
Peak :: \x.(EQUAL(x, peak))
Pennsylvania :: \x.(EQUAL(x, pennsylvania))
People :: \x.(people(x))
Pittsburgh :: \x.(EQUAL(x, pittsburgh))
Plano :: \x.(EQUAL(x, plano))
Platte :: \x.(EQUAL(x, platte))
Population :: \x.(population(x))
Portland :: \x.(EQUAL(x, portland))
Potomac :: \x.(EQUAL(x, potomac))
Red :: \x.(EQUAL(x, red))
Rhode :: \x.(EQUAL(x, rhode))
Rio :: \x.(EQUAL(x, rio))
Rivers :: \x.(rivers(x))
Riverside :: \x.(EQUAL(x, riverside))
Rochester :: \x.(EQUAL(x, rochester))
Rouge :: \x.(EQUAL(x, rouge))
Sacramento :: \x.(EQUAL(x, sacramento))
Salem :: \x.(salem(x))
Salt :: \x.(EQUAL(x, salt))
San :: \x.(EQUAL(x, san))
Scotts :: \x.(EQUAL(x, scotts))
Seattle :: \x.(EQUAL(x, seattle))
Show :: \x.(EQUAL(x, show))
South :: \x.(EQUAL(x, south))
Spokane :: \x.(EQUAL(x, spokane))
Springfield :: \x.(EQUAL(x, springfield))
State :: \x.(EQUAL(x, state))
States :: \x.(EQUAL(x, states))
Tell :: \B C e. exists y z .(tell:1(e, y) & tell:2(e, z) & C(y) & B(z))
Tempe :: \x.(EQUAL(x, tempe))
Tennessee :: \x.(EQUAL(x, tennessee))
Texas :: \x.(EQUAL(x, texas))
Through :: \B C y e. exists z .(C(through:1(e, y)) & C(through:2(e, z)) & C(y) & B(z))
Tucson :: \x.(EQUAL(x, tucson))
US :: \x.(EQUAL(x, us))
USA :: \x.(EQUAL(x, usa))
United :: \x.(EQUAL(x, united))
Utah :: \x.(EQUAL(x, utah))
Valley :: \x.(EQUAL(x, valley))
Vermont :: \x.(EQUAL(x, vermont))
Virginia :: \x.(EQUAL(x, virginia))
Washington :: \x.(EQUAL(x, washington))
Wayne :: \x.(EQUAL(x, wayne))
West :: \x.(EQUAL(x, west))
What :: \P. exists x.(TARGET(x) & P(x))
What :: \P Q x. exists e.(P(x,e) & Q(x))
Where :: \P. exists x.(TARGET(x) & P(x))
Where :: \P Q x. exists e.(P(x,e) & Q(x))
Which :: \P. exists x.(TARGET(x) & P(x))
Which :: \P Q x. exists e.(P(x,e) & Q(x))
Whitney :: \x.(EQUAL(x, whitney))
Wisconsin :: \x.(EQUAL(x, wisconsin))
Wyoming :: \x.(EQUAL(x, wyoming))
York :: \x.(EQUAL(x, york))
a :: None
about :: \B C y e. exists z .(C(about:1(e, y)) & C(about:2(e, z)) & C(y) & B(z))
adjacent :: \P x.(P(adjacent(x)) & P(x))
adjoin :: \P x.(P(adjoin(x)) & P(x))
and :: \P Q x.(P(x) & Q(x))
are :: \P R. exists x.(R(x) & P(x))
are :: \P x.(P(x))
area :: \x.(area(x))
at :: \B C y e. exists z .(C(at:1(e, y)) & C(at:2(e, z)) & C(y) & B(z))
average :: \P x.(P(average(x)) & P(x))
big :: \P x.(P(big(x)) & P(x))
biggest :: \P x.(P(biggest(x)) & P(x))
border :: \x.(border(x))
bordering :: \B C e. exists y z .(bordering:1(e, y) & bordering:2(e, z) & C(y) & B(z))
bordering :: \x.(bordering(x))
bordering :: \B e. exists y .(bordering:1(e, y) & B(y))
borders :: \x.(borders(x))
by :: \B C y e. exists z .(C(by:1(e, y)) & C(by:2(e, z)) & C(y) & B(z))
called :: \B C e. exists y z .(called:1(e, y) & called:2(e, z) & C(y) & B(z))
capital :: \x.(capital(x))
capitals :: \x.(capitals(x))
cities :: \x.(cities(x))
citizens :: \x.(citizens(x))
city :: \x.(city(x))
combined :: \B e. exists y .(combined:1(e, y) & B(y))
combined :: \P x.(P(combined(x)) & P(x))
contain :: \B C e. exists y z .(contain:1(e, y) & contain:2(e, z) & C(y) & B(z))
contains :: \B C e. exists y z .(contains:1(e, y) & contains:2(e, z) & C(y) & B(z))
continental :: \P x.(P(continental(x)) & P(x))
country :: \x.(country(x))
cross :: \B C e. exists y z .(cross:1(e, y) & cross:2(e, z) & C(y) & B(z))
cross :: \x.(cross(x))
dense :: \P x.(P(dense(x)) & P(x))
densities :: \x.(densities(x))
density :: \x.(density(x))
do :: \B C e. exists y z .(do:1(e, y) & do:2(e, z) & C(y) & B(z))
does :: \B C e. exists y z .(does:1(e, y) & does:2(e, z) & C(y) & B(z))
elevation :: \x.(elevation(x))
elevations :: \x.(elevations(x))
exist :: \B C e. exists y z .(exist:1(e, y) & exist:2(e, z) & C(y) & B(z))
fewest :: \P x.(P(fewest(x)) & P(x))
flow :: \x.(flow(x))
flow :: \B C e. exists y z .(flow:1(e, y) & flow:2(e, z) & C(y) & B(z))
flow :: \B e. exists y .(flow:1(e, y) & B(y))
flowing :: \B e. exists y .(flowing:1(e, y) & B(y))
flows :: \B e. exists y .(flows:1(e, y) & B(y))
flows :: \B C e. exists y z .(flows:1(e, y) & flows:2(e, z) & C(y) & B(z))
for :: \B C y e. exists z .(C(for:1(e, y)) & C(for:2(e, z)) & C(y) & B(z))
found :: \B e. exists y .(found:1(e, y) & B(y))
go :: \B C e. exists y z .(go:1(e, y) & go:2(e, z) & C(y) & B(z))
goes :: \B C e. exists y z .(goes:1(e, y) & goes:2(e, z) & C(y) & B(z))
greatest :: \P x.(P(greatest(x)) & P(x))
has :: \B C e. exists y z .(has:1(e, y) & has:2(e, z) & C(y) & B(z))
have :: \B C e. exists y z .(have:1(e, y) & have:2(e, z) & C(y) & B(z))
have :: \B e. exists y .(have:1(e, y) & B(y))
height :: \x.(height(x))
high :: \P x.(P(high(x)) & P(x))
higher :: \P x.(P(higher(x)) & P(x))
highest :: \P x.(P(highest(x)) & P(x))
how :: \P. exists x.(TARGET(x) & P(x))
how :: \P Q x. exists e.(P(x,e) & Q(x))
in :: \B C y e. exists z .(C(in:1(e, y)) & C(in:2(e, z)) & C(y) & B(z))
inhabitants :: \x.(inhabitants(x))
is :: \P R. exists x.(R(x) & P(x))
is :: \P x.(P(x))
it :: \x.(EQUAL(x, it))
kilometers :: \x.(kilometers(x))
km :: \x.(km(x))
lakes :: \x.(lakes(x))
large :: \P x.(P(large(x)) & P(x))
largest :: \P x.(P(largest(x)) & P(x))
least :: \P x.(P(least(x)) & P(x))
length :: \x.(length(x))
level :: \x.(level(x))
lie :: \B e. exists y .(lie:1(e, y) & B(y))
live :: \B e. exists y .(live:1(e, y) & B(y))
lived :: \B e. exists y .(lived:1(e, y) & B(y))
located :: \B e. exists y .(located:1(e, y) & B(y))
located :: \B C e. exists y z .(located:1(e, y) & located:2(e, z) & C(y) & B(z))
long :: \P x.(P(long(x)) & P(x))
longest :: \P x.(P(longest(x)) & P(x))
lower :: \P x.(P(lower(x)) & P(x))
lowest :: \P x.(P(lowest(x)) & P(x))
major :: \P x.(P(major(x)) & P(x))
many :: \P x.(P(many(x)) & P(x))
maximum :: \P x.(P(maximum(x)) & P(x))
me :: \x.(EQUAL(x, me))
meters :: \x.(meters(x))
miles :: \x.(miles(x))
most :: \P x.(P(most(x)) & P(x))
mountain :: \x.(mountain(x))
mountains :: \x.(mountains(x))
much :: \P x.(P(much(x)) & P(x))
name :: \x.(name(x))
named :: \B C e. exists y z .(named:1(e, y) & named:2(e, z) & C(y) & B(z))
names :: \x.(names(x))
neighbor :: \x.(neighbor(x))
neighboring :: \P x.(P(neighboring(x)) & P(x))
next :: \P x.(P(next(x)) & P(x))
no :: \P x.(COMPLEMENT(x) & P(x))
not :: \P Q e. exists x.(NEGATION(e) & P(e,x) & Q(x))
number :: \x.(number(x))
of :: \B C y e. exists z .(C(of:1(e, y)) & C(of:2(e, z)) & C(y) & B(z))
on :: \B C y e. exists z .(C(on:1(e, y)) & C(on:2(e, z)) & C(y) & B(z))
one :: \x.(EQUAL(x, one))
one :: \P x.(COUNT(x, one) & P(x))
one :: \x.(one(x))
or :: \P Q x.(P(x) & Q(x))
other :: \P x.(P(other(x)) & P(x))
over :: \B C y e. exists z .(C(over:1(e, y)) & C(over:2(e, z)) & C(y) & B(z))
pass :: \B C e. exists y z .(pass:1(e, y) & pass:2(e, z) & C(y) & B(z))
passes :: \B e. exists y .(passes:1(e, y) & B(y))
passes :: \B C e. exists y z .(passes:1(e, y) & passes:2(e, z) & C(y) & B(z))
peak :: \x.(peak(x))
people :: \x.(people(x))
per :: \B C y e. exists z .(C(per:1(e, y)) & C(per:2(e, z)) & C(y) & B(z))
point :: \x.(point(x))
points :: \x.(points(x))
populated :: \P x.(P(populated(x)) & P(x))
population :: \x.(population(x))
populations :: \x.(populations(x))
populous :: \P x.(P(populous(x)) & P(x))
reside :: \B C e. exists y z .(reside:1(e, y) & reside:2(e, z) & C(y) & B(z))
residents :: \x.(residents(x))
river :: \x.(river(x))
rivers :: \x.(rivers(x))
run :: \B e. exists y .(run:1(e, y) & B(y))
run :: \B C e. exists y z .(run:1(e, y) & run:2(e, z) & C(y) & B(z))
run :: \x.(run(x))
running :: \B e. exists y .(running:1(e, y) & B(y))
runs :: \x.(runs(x))
runs :: \B C e. exists y z .(runs:1(e, y) & runs:2(e, z) & C(y) & B(z))
runs :: \B e. exists y .(runs:1(e, y) & B(y))
s :: \B C D e. exists z v y .(_s:1(e, z) & _s:2(e, v) & _s:3(e, y) & D(z) & C(v) & B(y))
s :: \B C e. exists y z .(_s:1(e, y) & _s:2(e, z) & C(y) & B(z))
sea :: \x.(sea(x))
shortest :: \P x.(P(shortest(x)) & P(x))
size :: \x.(size(x))
smallest :: \P x.(P(smallest(x)) & P(x))
sparsest :: \P x.(P(sparsest(x)) & P(x))
spot :: \x.(spot(x))
square :: \P x.(P(square(x)) & P(x))
state :: \x.(state(x))
states :: \x.(states(x))
stay :: \B e. exists y .(stay:1(e, y) & B(y))
surround :: \B C e. exists y z .(surround:1(e, y) & surround:2(e, z) & C(y) & B(z))
surrounding :: \B C e. exists y z .(surrounding:1(e, y) & surrounding:2(e, z) & C(y) & B(z))
surrounding :: \B e. exists y .(surrounding:1(e, y) & B(y))
tall :: \P x.(P(tall(x)) & P(x))
tallest :: \P x.(P(tallest(x)) & P(x))
tell :: \B C e. exists y z .(tell:1(e, y) & tell:2(e, z) & C(y) & B(z))
tell :: \B C D e. exists y z w .(tell:1(e, y) & tell:2(e, z) & tell:3(e, w) & D(y) & C(z) & B(w))
than :: \B C y e. exists z .(C(than:1(e, y)) & C(than:2(e, z)) & C(y) & B(z))
that :: \P. exists x.(TARGET(x) & P(x))
that :: \P Q x. exists e.(P(x,e) & Q(x))
that :: \B C y e. exists z .(C(that:1(e, y)) & C(that:2(e, z)) & C(y) & B(z))
the :: \P x.(UNIQUE(x) & P(x))
them :: \x.(EQUAL(x, them))
through :: \B C y e. exists z .(C(through:1(e, y)) & C(through:2(e, z)) & C(y) & B(z))
to :: \B C e. exists y w .(to:1(e, y) & to:2(e, w) & C(y) & B(w))
to :: \B e. exists y .(to:1(e, y) & B(y))
total :: \P x.(P(total(x)) & P(x))
towns :: \x.(towns(x))
traverse :: \B C e. exists y z .(traverse:1(e, y) & traverse:2(e, z) & C(y) & B(z))
traversed :: \B e. exists y .(traversed:1(e, y) & B(y))
traverses :: \B C e. exists y z .(traverses:1(e, y) & traverses:2(e, z) & C(y) & B(z))
traverses :: \B C D e. exists y z w .(traverses:1(e, y) & traverses:2(e, z) & traverses:3(e, w) & D(y) & C(z) & B(w))
traverses :: \x.(traverses(x))
urban :: \P x.(P(urban(x)) & P(x))
washed :: \B e. exists y .(washed:1(e, y) & B(y))
what :: \P. exists x.(TARGET(x) & P(x))
what :: \P Q x. exists e.(P(x,e) & Q(x))
which :: \P. exists x.(TARGET(x) & P(x))
which :: \P Q x. exists e.(P(x,e) & Q(x))
whose :: \P. exists x.(TARGET(x) & P(x))
whose :: \P Q x. exists e.(P(x,e) & Q(x))
with :: \B C y e. exists z .(C(with:1(e, y)) & C(with:2(e, z)) & C(y) & B(z))
you :: \x.(EQUAL(x, you))
# CATEGORIES
N :: \x.(EQUAL(x, {0}))
N :: \x.({0}(x))
N :: \P x.(P({0}(x)) & P(x))
NP :: \x.(EQUAL(x, {0}))
S/S :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
S/S :: \P. exists x.(TARGET(x) & P(x))
S/S :: \P Q x. exists e.(P(x,e) & Q(x))
S/S :: \x.({0}(x))
S\S :: \x.(EQUAL(x, {0}))
N/N :: \x.(EQUAL(x, {0}))
N/N :: \P x.(P({0}(x)) & P(x))
N/N :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
N/N :: \P x.(COUNT(x, {0}) & P(x))
N/N :: \x.({0}(x))
N/N :: \B e. exists y .({0}:1(e, y) & B(y))
N/N :: \P x.(UNIQUE(x) & P(x))
NP/N :: \P. exists x.(TARGET(x) & P(x))
NP/N :: \P Q x. exists e.(P(x,e) & Q(x))
NP/N :: \P x.(P({0}(x)) & P(x))
NP/N :: \P x.(COMPLEMENT(x) & P(x))
NP/N :: None
NP/N :: \P x.(UNIQUE(x) & P(x))
conj :: \P Q x.(P(x) & Q(x))
S\NP :: \B e. exists y .({0}:1(e, y) & B(y))
S\NP :: \P x.(P({0}(x)) & P(x))
S\NP :: \x.({0}(x))
NP\NP :: \x.(EQUAL(x, {0}))
NP\NP :: \P Q e. exists x.(NEGATION(e) & P(e,x) & Q(x))
NP\NP :: \x.({0}(x))
PP/NP :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
PP/NP :: \B e. exists y .({0}:1(e, y) & B(y))
(S\S)/N :: \P x.(UNIQUE(x) & P(x))
(N\N)/NP :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
S/(S\NP) :: \P. exists x.(TARGET(x) & P(x))
S/(S\NP) :: \P Q x. exists e.(P(x,e) & Q(x))
(S\NP)/S :: \x.({0}(x))
(S\S)/NP :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
S/(S/NP) :: \P. exists x.(TARGET(x) & P(x))
S/(S/NP) :: \P Q x. exists e.(P(x,e) & Q(x))
S/(S/PP) :: \P. exists x.(TARGET(x) & P(x))
S/(S/PP) :: \P Q x. exists e.(P(x,e) & Q(x))
(S/NP)/NP :: \P R. exists x.(R(x) & P(x))
(S/NP)/NP :: \P x.(P(x))
(S\NP)/PP :: \B C e. exists y z .({0}:1(e, y) & {0}:2(e, z) & C(y) & B(z))
(S\NP)/PP :: \P R. exists x.(R(x) & P(x))
(S\NP)/PP :: \P x.(P(x))
(S\NP)/PP :: \P x.(P({0}(x)) & P(x))
(S\NP)/PP :: \x.({0}(x))
(S\NP)\NP :: \P x.(P({0}(x)) & P(x))
(S/PP)/NP :: \P R. exists x.(R(x) & P(x))
(S/PP)/NP :: \P x.(P(x))
(S/PP)/NP :: \B C e. exists y z .({0}:1(e, y) & {0}:2(e, z) & C(y) & B(z))
NP/(S/NP) :: \P. exists x.(TARGET(x) & P(x))
NP/(S/NP) :: \P Q x. exists e.(P(x,e) & Q(x))
(NP\NP)/S :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
(NP\NP)/S :: \P. exists x.(TARGET(x) & P(x))
(NP\NP)/S :: \P Q x. exists e.(P(x,e) & Q(x))
(S\NP)/NP :: \P x.(P({0}(x)) & P(x))
(S\NP)/NP :: \B C e. exists y z .({0}:1(e, y) & {0}:2(e, z) & C(y) & B(z))
(S\NP)/NP :: \P R. exists x.(R(x) & P(x))
(S\NP)/NP :: \P x.(P(x))
(NP\NP)/N :: \P x.(UNIQUE(x) & P(x))
NP/(S\NP) :: \P. exists x.(TARGET(x) & P(x))
NP/(S\NP) :: \P Q x. exists e.(P(x,e) & Q(x))
(NP\NP)/NP :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
(N/N)/(N/N) :: \P x.(P({0}(x)) & P(x))
(S/(S/NP))/N :: \P. exists x.(TARGET(x) & P(x))
(S/(S/NP))/N :: \P Q x. exists e.(P(x,e) & Q(x))
(S/(S\NP))/N :: \P. exists x.(TARGET(x) & P(x))
(S/(S\NP))/N :: \P Q x. exists e.(P(x,e) & Q(x))
(S\(S/NP))/N :: \P. exists x.(TARGET(x) & P(x))
(S\(S/NP))/N :: \P Q x. exists e.(P(x,e) & Q(x))
(NP/(S\NP))/N :: \P. exists x.(TARGET(x) & P(x))
(NP/(S\NP))/N :: \P Q x. exists e.(P(x,e) & Q(x))
(S\NP)\(S\NP) :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
(S\NP)\(S\NP) :: \x.(EQUAL(x, {0}))
(S\NP)\(S\NP) :: \P Q e. exists x.(NEGATION(e) & P(e,x) & Q(x))
(S\NP)\(S\NP) :: \x.({0}(x))
(S\NP)/(S\NP) :: \B C e. exists y z .({0}:1(e, y) & {0}:2(e, z) & C(y) & B(z))
(S\NP)/(S\NP) :: \P R. exists x.(R(x) & P(x))
(S\NP)/(S\NP) :: \P x.(P(x))
(S\NP)/(S\NP) :: \x.({0}(x))
(S\NP)/(S\NP) :: \P. exists x.(TARGET(x) & P(x))
(S\NP)/(S\NP) :: \P Q x. exists e.(P(x,e) & Q(x))
(S/(S\NP))/NP :: \B C e. exists y z .({0}:1(e, y) & {0}:2(e, z) & C(y) & B(z))
(S/(S\NP))/NP :: \P R. exists x.(R(x) & P(x))
(S/(S\NP))/NP :: \P x.(P(x))
(S/(S\NP))/NP :: \P. exists x.(TARGET(x) & P(x))
(S/(S\NP))/NP :: \P Q x. exists e.(P(x,e) & Q(x))
((S\NP)/NP)/NP :: \B C D e. exists y z w .({0}:1(e, y) & {0}:2(e, z) & {0}:3(e, w) & D(y) & C(z) & B(w))
((S\NP)/PP)/NP :: \B C D e. exists y z w .({0}:1(e, y) & {0}:2(e, z) & {0}:3(e, w) & D(y) & C(z) & B(w))
(NP\NP)/(S\NP) :: \P. exists x.(TARGET(x) & P(x))
(NP\NP)/(S\NP) :: \P Q x. exists e.(P(x,e) & Q(x))
(NP\NP)/(S\NP) :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
(NP\NP)/(S/NP) :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
(NP\NP)/(NP\NP) :: \x.(EQUAL(x, {0}))
(NP\NP)/(NP\NP) :: \x.({0}(x))
((S/PP)/N)/(NP/N) :: \P. exists x.(TARGET(x) & P(x))
((S/PP)/N)/(NP/N) :: \P Q x. exists e.(P(x,e) & Q(x))
((S\NP)\(S\NP))/N :: \P x.(COMPLEMENT(x) & P(x))
((S\NP)\(S\NP))/N :: \P x.(UNIQUE(x) & P(x))
((S\NP)/(S\NP))/NP :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
((NP\NP)/(S\NP))/N :: \P. exists x.(TARGET(x) & P(x))
((NP\NP)/(S\NP))/N :: \P Q x. exists e.(P(x,e) & Q(x))
((S\NP)\(S\NP))/NP :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
((S\NP)\(S\NP))/NP :: \B C e. exists y w .({0}:1(e, y) & {0}:2(e, w) & C(y) & B(w))
((N/N)/(N/N))/(S\NP) :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
(S/(S/PP))/(S/(S/NP)) :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
((S/(S\NP))/N)/(NP/N) :: \P. exists x.(TARGET(x) & P(x))
((S/(S\NP))/N)/(NP/N) :: \P Q x. exists e.(P(x,e) & Q(x))
((S/(S/NP))/N)/(NP/N) :: \P. exists x.(TARGET(x) & P(x))
((S/(S/NP))/N)/(NP/N) :: \P Q x. exists e.(P(x,e) & Q(x))
(S/(S/(S\NP)))/(S\NP) :: \P. exists x.(TARGET(x) & P(x))
(S/(S/(S\NP)))/(S\NP) :: \P Q x. exists e.(P(x,e) & Q(x))
(S/(S/NP))/(S/(S/NP)) :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
((NP\NP)/S)\((NP\NP)/NP) :: \P. exists x.(TARGET(x) & P(x))
((NP\NP)/S)\((NP\NP)/NP) :: \P Q x. exists e.(P(x,e) & Q(x))
((S/(S\NP))/N)\(S/(S\NP)) :: \B C D e. exists z v y .({0}:1(e, z) & {0}:2(e, v) & {0}:3(e, y) & D(z) & C(v) & B(y))
(((S/PP)/((S/PP)/NP))/N)/(NP/N) :: \P. exists x.(TARGET(x) & P(x))
(((S/PP)/((S/PP)/NP))/N)/(NP/N) :: \P Q x. exists e.(P(x,e) & Q(x))
((S\NP)\(S\NP))/((S\NP)\(S\NP)) :: \B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))
(((S\NP)\(S\NP))\((S\NP)\(S\NP)))/N :: \P x.(UNIQUE(x) & P(x))
