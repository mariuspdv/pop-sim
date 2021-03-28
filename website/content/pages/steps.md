Lang: fr
Order: C
Title: Etapes
Slug: steps
Author: Marius Poudevigne
Summary: Les étapes du modèle

# Détermination des prix et production
Tout d’abord, l’entreprise connaît les caractéristiques suivantes : son nombre d'employés de chaque type, leurs salaires, sa valeur de productivité intrinsèque, les profits et prix précédents, les stocks restants et son compte en banque. A partir de ces informations, elle va devoir décider de son prix et de sa production cible. Une fois ces cibles fixées, elle en déduira sa demande de travail.
Le choix de la production cible et du prix prend seulement deux éléments en compte : les profits précédents et les stocks restants (avant production). C’est un tâtonnement basé sur les prix et production précédents, dont on s’éloigne par incréments proportionnels. L’idée est que l’entreprise n’a pas nécessairement des informations très détaillées sur la demande future pour son produit, et prend des décisions à vue pour essayer de diminuer ses stocks et maximiser son profit. En utilisant uniquement ces deux indicateurs, on a donc quatre possibilités :

|             | **Stocks nuls** | **Stocks positifs** |
|-------------|-----------------|---------------------|
| **Pertes**      | L’entreprise écoule bien ce qu’elle produit, mais ne fait pas de profit, le prix doit donc augmenter, au moins jusqu’au coût unitaire, et la production reste la même | Tout va mal, la marchandise ne s’écoule pas et l’entreprise fait des pertes. Dans ce cas-là, l’entreprise diminue la production (il reste déjà du stock à écouler, et les coûts doivent diminuer) et diminue le prix tant que celui-ci reste supérieur au coût unitaire afin d’écouler les stocks |
| **Profits**     | L’entreprise écoule sa production et fait même des profits. Si ces profits donnent une marge suffisante, la production cible augmente, mais si la marge idéale n’est pas encore atteinte, le prix augmente | Malgré les profits, s’il y a des stocks qui s’empilent, il y a de l’optimisation possible. Si les stocks sont petits, alors une légère diminution du prix sans changer la production devrait être suffisante. S’ils sont larges, alors l’entreprise baisse à la fois sa production cible et son prix |

Les diminutions/augmentations de prix et de production cible ici sont relatives, par pourcentages fixes et déterminés de manière exogène. Il s’agit pour moi d’une vraie marge de progression du modèle : une étude plus précise du comportement des entreprises et des paramètres plus réalistes et nuancés. Cependant, bien que ce comportement soit central aux résultats finaux du modèle, je pense que la direction des choix et la justification est suffisante pour une maquette.

_____________________

# Marché du travail 

## Demande de travail

La demande de travail découle de la production ciblée et du processus de production de l’entreprise. Plongeons-nous donc dans ce dernier. Tout d’abord, une entreprise produit sans capital (pour l’instant) et avec deux types d’employés, qui sont aussi des types de pop différents :

- les travailleurs « blue collar », qui produisent le bien de l’entreprise (un blue collar produit x unités de bien en un tick, pour x la valeur finale de productivité de l’entreprise)
- les travailleurs « white collar », qui représentent les cadres et autres travailleurs « qualifiés » dans le jargon économique plus classique, qui modifient la productivité de l’entreprise

La productivité de l’entreprise est une productivité intrinsèque immuable que l’on multiplie par un bonus de productivité. Ce bonus de productivité dépend du ratio white/blue collar dans l'entreprise. Précisément, chaque entreprise possède un ratio idéal où le bonus de productivité est maximisé, et ce bonus est croissant avec des gains marginalement décroissants jusqu’au ratio idéal, après lequel le bonus est plafonné. Les white collars au-dessus de ce ratio seront donc inutiles.

Maintenant que le processus de production est clair, il est facile de le combiner avec la production ciblée pour obtenir les demandes de travail. Pour les blue collar, l’entreprise part du principe qu'elle réussira à maintenir son précédent niveau de productivité. Avec cette supposition, la demande pour les blue collar est simplement le résultat d’une division de la production cible par la productivité.

La demande pour les white collar est déterminée une fois le marché pour les blue collar résolu, car l’entreprise ne réussit pas toujours à embaucher le nombre d’employés désirés. Avec cette information, l’entreprise tente d'embaucher des white collar jusqu'à ce que le rapport cout-bénéfice soit négatif, c’est-à-dire lorsque le white collar marginal permettra à l'entreprise de produire autant de valeur que son salaire.

_____________________
 
## Fonctionnement du marché

Une fois la demande de travail calculée pour chaque entreprise, celles-ci peuvent aller sur le marché du travail. Ou plutôt devrais-je dire les marchés du travail. Pour comprendre la logique de ce marché, il faut rappeler que l'objectif de ce modèle est de s'affranchir autant que possible de lois générales et de forces du marché pour revenir à une série de « micro-transactions » et regarder leur effet global. Il ne fallait donc pas organiser les marchés sous le principe d'une offre-demande globale avec un équilibre unique, comme dans un exercice de microéconomie, ni intégrer artificiellement l’état global du marché dans les négociations individuelles. Enfin, la division des marchés du travail entre blue et white collar était nécessaire dans le modèle. Elle ajoute une dose de réalisme et une possibilité d’étendre encore davantage la simulation avec des marchés du travail plus nombreux et spécifiques à des secteurs ou compétences, pour une compréhension plus fine du chômage.

Le marché est résolu firme par firme, dans un ordre aléatoire. Pour chacune d’entre elles, il faut simplement :

1. déterminer sa demande de travail
2. déterminer son offre de travail (qui fait partie de sa “labor pool”)
3. tirer au sort un individu dans cette offre et ajuster le salaire moyen
4. recommencer jusqu’à épuisement de l’offre ou de la demande

Plus en détails, cela nous donne: une entreprise est d’abord tirée au sort, et sa demande est déterminée. Si sa demande est positive, elle va chercher à embaucher sur le marché. Cependant, l’offre de travail (labor pool dans le modèle) n’est pas la même pour toutes les entreprises. Elle comprend tous les chômeurs du type d’employé désiré, mais aussi tous les employés d’autres entreprises dont le salaire pour ce type d’employé est inférieur ou égal. Si cette offre est vide, l’entreprise ouvre sa recherche aux travailleurs payés plus chers que chez elle, dans une certaine limite. En effet, chaque entreprise a une valeur de salaire pour chaque type de travailleur, qui représente le salaire moyen de ces travailleurs dans l’entreprise.

L’entreprise va ensuite tirer un individu au sort dans toute cette offre (avec équiprobabilité entre individus). Si elle tire un chômeur, elle l’engagera à un salaire un peu inférieur à son salaire moyen, pour représenter le rapport de force des négociations et les autres facteurs possibles – perte de compétence, signalling, etc. Si elle tire un travailleur d’une autre entreprise, elle l’engagera à un salaire un peu supérieur à son salaire précédent. Quoi qu’il arrive, le salaire moyen est ajusté et l’entreprise continue jusqu’à épuisement de la labor pool ou saturation de sa demande de travail.

Une fois que l'entreprise a fini, on en tire une autre au sort, et ainsi de suite. La même entreprise ne peut pas être piochée de nouveau. Certaines firmes ayant déjà fini leur tour d'embauche se feront donc parfois débaucher des employés et termineront en deçà de leur objectif d’employés. Bien sûr, cela arrivera plus souvent aux entreprises qui payent sous le prix du marché, particulièrement en temps de plein emploi, car leurs travailleurs seront plus souvent inclus dans l’offre de travail des autres entreprises. Cela représente bien certaines frictions sur le marché du travail, et le tirage au sort fait que toutes les entreprises peuvent y être sujettes, pas toujours les mêmes.

### Discussion
Plusieurs choix peuvent être mis en cause dans ce modèle. L'idée des incréments de salaire n'est pas très subtile, mais permet d'éviter d'intégrer artificiellement des lois de marché (avec par exemple des incréments qui dépendraient du taux de chômage global). D’ailleurs, on peut voir dans les simulations une corrélation entre la hausse ou baisse des salaires et le taux de chômage qui émerge naturellement. Le fait que les entreprises aient une seule valeur de salaire est aussi un long sujet de réflexion : se souvenir de chaque contrat paraît intuitivement plus réaliste, mais crucialement changerait l’interprétation du modèle. En effet, le pop représente des individus « interchangeables » dans le sens de la simulation, comme une communauté. Si chaque contrat était spécifique à un individu, il faudrait se souvenir d’autres facteurs (retraites, changements, etc.) et radicalement changer d’autres fonctionnements de la simulation pour se recentrer sur les individus.

_____________________
 
# Production et paiements

Les entreprises ont donc déterminé les moyens de production à leur disposition sur cette période. Elles peuvent donc produire et ajouter le tout à leurs stocks, et payer ce qu’elles doivent aux salariés et actionnaires. Le mécanisme de production a déjà été expliqué, et est purement déterministe maintenant que les entreprises ont leur nombre d'employés. Ce que les entreprises produisent est ajouté à leur stock. Elles paient ensuite leurs salaires, qui sont répartis dans les différents pops sous forme de revenus selon le nombre d’individus de chaque pop employés dans chaque entreprise.

Elles vont enfin payer leurs actionnaires d'après les dividendes déterminés à la fin de la période précédente. Si elles ont fait des profits et qu'elles n'étaient pas endettées, alors la moitié de ces profits est distribuée à leurs actionnaires et reversée aux pops selon les parts qu'ils détiennent. Les pops peuvent donc aborder le marché des biens avec leurs revenus, mais il reste à étudier leur demande, ou plutôt leurs besoins.

_____________________
 
# Marché des biens

## Besoins

Pour comprendre le marché des biens il faut s'attarder sur la demande. Elle est déterminée par les besoins (needs dans le modèle) des pops. Que sont les besoins ? Ce sont des caractéristiques immuables. Il s'agit de quantités fixes de chaque bien, pour chaque individu du pop, sur plusieurs niveaux. Chaque niveau représente un degré différent de ce qui est nécessaire pour bien vivre, similaire au principe de la pyramide de Maslow. Ainsi le plus bas niveau comprend l'alimentation, le logement et de quoi se vêtir. Chaque niveau ensuite ajoute de ces besoins de base mais également de nouveaux produits, pour l'instant groupés sous l'appellation « luxe ». Le premier niveau représente les besoins fondamentaux d’un individu, ce sans quoi cette personne ne peut pas vivre. Par conséquent, la priorité des pops sera de remplir ce premier niveau à tout prix.

Ce principe de besoin peut être diversifié avec bien plus de biens et de niveaux. Idéalement, il serait basé sur des études de consommation de groupes différents. Une des raisons principales de la division en pops dans cette simulation est la croyance qu’il existe, sur le domaine de la consommation, des groupes qui sont régis par des comportements similaires. Ainsi, les besoins de chaque pop seront différents. 

 
## Passage à la caisse

Pour conceptualiser le marché des biens, il faut imaginer un immense supermarché, où tous les biens et toutes les marques sont disponibles et toute notre population se masse et fait la queue. L’offre dans le supermarché est simplement tous les stocks de toutes les entreprises de l’économie, au prix qu’elles ont chacune déterminé au début du tick. C’est dans la constitution de la queue que réside toute la subtilité du marché.

Tout d’abord, on résout les besoins niveau par niveau. On va ainsi commencer par comptabiliser tous les besoins fondamentaux des pops en chaque bien. Fonctionner par niveau est un choix discutable, mais nécessaire ici : la demande des pops est inélastique à chaque niveau, ainsi il leur faut remplir ces besoins niveau par niveau. On peut imaginer que les individus se pressent d’assurer leur subsistance - bien qu’évidemment les commodités en offre restreinte ne vont pas toujours à ceux qui en ont le plus besoin dans le monde réel.

On divise ensuite cette demande totale en “paniers” de taille égale, chaque panier étant d’un seul bien pour un pop. Ces paniers vont tous passer à la caisse les uns après les autres, dans un ordre aléatoire. Une fois tous les paniers épuisés, on passe au niveau suivant et on répète.

A la caisse, chacun va déterminer aléatoirement à quelle entreprise ils vont acheter, mais où la probabilité de tirer une firme est inversement proportionnelle à son prix. Ceci permet de modéliser des préférences de marque ou de disponibilité, qui font que les consommateurs achètent parfois à des marques moins compétitives. Une fois le choix fait, la transaction se fait immédiatement, et l’argent se transfère directement sur le compte de l’entreprise vendeuse. 

Si le pop n’a plus assez dans ses revenus pour acheter le produit, il en achète la proportion restante et s’arrête de consommer. Cependant, si cela arrive au premier niveau de besoins, le pop ira tirer dans son épargne pour compléter, afin de ne pas tomber sous le seuil de survie. En effet, le premier niveau représente les besoins fondamentaux et cela permet de modéliser une impossibilité de diminuer sa consommation en-dessous d’un certain seuil, sous peine de famine.

Pour les autres niveaux de besoin, on procède de la même manière jusqu'à ce que personne ne puisse plus acheter, ou qu'il n'y ait plus rien à vendre pour un bien donné. Pour ces niveaux, les pops ne peuvent pas dépenser leur épargne. Enfin, cette épargne est amassée  lorsqu’il reste des revenus à un pop après le premier niveau. Une proportion fixe et exogène des revenus restants est mise de côté une fois la survie assurée. Si jamais le pop s’endette, ce qui est autorisé sous contraintes pour remplir ses besoins de premier niveau, tous ses revenus au-dessus de ces premiers besoins seront dédiés au remboursement des dettes.

_____________________
 
# Entreprises et financement

## Comptabilité et finance

Les mécanismes principaux ont été illustrés, mais il reste à expliquer quelques points techniques de comptabilité et d’ajout des intérêts. Le modèle n'est pas complet dans le sens où il n'y a pas vraiment de système bancaire : les dettes ne sont pas dues à qui que ce soit et les contraintes à l'emprunt sont des règles, pas des choix d’agents. Cependant, je pense pouvoir illustrer déjà suffisamment de phénomènes sans un marché de l’épargne développé pour une première maquette.

Tous nos agents ont un compte bancaire, qu’on autorise à aller dans les négatifs, c’est-à-dire à emprunter. Les emprunts se font à une banque centralisée qui définit le taux d’intérêt de manière exogène pour toute l’économie. Ainsi, à la fin de chaque tick, tous les comptes sont ajustés pour les intérêts. Pour éviter l’endettement excessif, les pops sont averses à accumuler de la dette et les entreprises qui s’enfoncent trop font faillite. Un système financier ou des comportements vis-à-vis de l’épargne plus développés ne seraient pourtant pas de trop, notamment pour gérer l’épargne accumulée qui pour l’instant est inefficace et prend la poussière dans les comptes en banque.
 
## Organiser la compétition

Ce système de comptabilité nous permet donc d’avoir un critère pour liquider et/ou créer des entreprises. Au début de chaque tick, toutes les entreprises dont les intérêts sur leurs emprunts sont inférieurs à leurs revenus (pas leurs profits, leur chiffre d'affaires), doivent mettre la clé sous la porte. Elles sont liquidées, virent tous leurs employés et vendent le reste de leur stock pour tenter de rembourser leurs dettes.

Si des firmes font faillite, d’autres doivent pouvoir voir le jour. Comment et quel type d’entreprise naît est l’issue d’un processus aléatoire. Sur chaque marché à chaque tick, un tirage est effectué. S’il n’y a plus d’entreprise active sur un marché, une nouvelle entreprise y voit le jour. Sinon, les chances de création d’entreprise croissent avec (a) les profits totaux sur le marché, (b) l’épargne des capitalistes et (c) la demande latente pour le produit, c’est-à-dire les besoins insatisfaits en ce produit. Ce n’est pas un processus déterministe car on peut imaginer que seule des estimations de ces informations sont disponibles aux acteurs pour prendre leur décision.

Dans la création de firmes, le capital vient des pops de type capitaliste, mais peut aussi venir de l'épargne d'autres pops si elle est suffisante, selon la propension à investir de ceux-ci. Ils détiendront alors des titres dans la nouvelle entreprise en fonction de leur investissement initial. Cet investissement initial va dans le compte de l'entreprise.
