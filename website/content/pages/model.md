Lang: fr
Order: B
Title: Modèle
Slug: model
Author: Marius Poudevigne
Summary: Description du modèle

# Structure de la simulation 

La simulation qui va suivre ne repose que sur deux types d’agents : les « pops » et les entreprises.  

![Overview](/images/model_overview.png)

# Présentation des agents

Un “pop” est un groupe d’individus qui partage des caractéristiques de comportement et va interagir comme un seul agent sur les marchés (sauf celui du travail). On pourrait cependant se poser la question : pourquoi ne pas avoir choisi les individus comme unité de base de simulation ?

Tout d’abord, il s’agit du niveau d’analyse qui me paraît le plus adapté pour la précision d’un modèle comme celui-ci. Les comportements individuels et les données disponibles ne permettent aucune prédiction au niveau des individus, mais un tel modèle se doit d’être plus précis qu’un agrégat général de tous les consommateurs d’une économie. Il peut être localisé à une région, une place dans le processus de production et un certain motif d’habitudes de consommation. On pourrait ainsi étudier la répartition des richesses après un certain choc entre des grands groupes sociologiques – cadres et employés – sans pouvoir pour autant comparer deux individus. De plus, le groupement en pops de comportements similaires permet aussi de refléter une réalité – avoir des groupes qui remplissent des fonctions différentes dans l’économie tout en ayant des comportements de consommation et d’épargne différents – sans avoir à gérer de nombreux mécanismes non-essentiels, comme les héritages, mariages, retraites, etc. Un pop comprend toute la population active d’un certain type d’individu. Enfin, on peut citer un problème de puissance. La simulation doit tourner sur un ordinateur portable, et le nombre d’interactions simulées - dans la forme actuelle non-optimisée du modèle - augmente exponentiellement avec le nombre d’agents. Pour commencer à observer des résultats intéressants il fallait limiter ce nombre.

![Overview](/images/pop_overview.png)

Les pops sont donc des groupes d’individus de taille variable (la population est une de leurs caractéristiques) qui ont des propriétés communes : type de travail, besoins similaires, mêmes interactions sur les différents marchés. Ils sont pour l’instant divisés en trois types simples : les « blue collar workers » (travailleurs non-qualifiés), « white collar workers » (travailleurs qualifiés) et les « capitalistes ». Il peut avoir plusieurs pops du même type, tant que les différences entre eux sont suffisamment importantes – habitudes de consommation par exemple, ici modélisées par les besoins. Nous entrerons dans les détails des propriétés et caractéristiques des pops lorsque nous aborderons leurs règles de décision.

Nos entreprises sont beaucoup plus faciles à aborder. Elles représentent une entreprise ou branche d’entreprise qui produit un unique bien. Elles ont quelques caractéristiques fondamentales et immuables : le bien produit, une valeur de productivité intrinsèque et un ratio idéal de type de pops à employer. A chaque temps de notre simulation, elles produisent, adaptent leur prix, emploient, vendent et enfin changent leurs stocks et leurs comptes. Elles ont également une structure de propriété propre, avec des actions distribuées parmi les différents pops.

_____________________

# Ordre des actions

Le modèle avance par « ticks », qui comprennent à chaque fois la même série d’actions :

Le tout se répète un nombre de fois déterminé à l’avance. 
![Overview](/images/tick_steps.png)

Cet ordre a été choisi pour que les agents aient à chaque période les informations nécessaires à leur choix : 
l’état comptable des entreprises et la demande précédente pour les deux premières étapes, la demande de travail pour les marchés du travail, les employés pour la production et enfin les stocks, prix et les revenus pour le marché des biens.
        	
La question encore en suspens est combien de temps un tick est censé représenter. Les ajustements étant relativement mineurs et à la marge, mais le temps de réaction reste relativement rapide – par exemple, la demande de travail d’une entreprise réagit aux données du précédent tick et influence immédiatement l’embauche. Un tick est à prendre comme quelques semaines, mais des incohérences sont encore à ajuster pour arriver à quelque chose de réaliste : idéalement, cela doit être adapté aux données que l’on peut recevoir (mensuellement ?) et aux études sur les comportements et délais des agents.

_____________________
 
# Agrégats

Enfin, afin d’essayer de comprendre ce qu’il se passe dans le modèle, nous avons intégré plusieurs capteurs qui nous permettent de calculer des agrégats macroéconomiques – PIB, inflation, etc. Il est important de les comprendre car ils seront utilisés énormément dans l’analyse de résultats de simulation, avec bien sûr les comptes et comportements des agents.

Le premier agrégat classique est le PIB. Il s’agit simplement de la somme de toutes les transactions de vente de produit dans un tick. Ce PIB est sujet au niveau de prix, et ne peut être interprété qu'en conjugaison avec celui-ci.

On a une mesure d'inflation, qui a nécessité le calcul d'une mesure de niveau de prix. Il est basé sur un panier de biens constitué de la moyenne des besoins de premier niveau dans l'économie. Il permet de calculer un PIB ajusté, en terme de paniers de biens de premier niveau que l'économie produit. Cela correspond à la population que l'économie peut soutenir au niveau de subsistance. S'il est inférieur à un, l'économie est en crise majeure. 
