# RocketTail - Documentação do Dataset

## Visão Geral

O **RocketTail** é um projeto de sistema de recomendação de produtos baseado em rede neural (MLP ou embedding-based), desenvolvido com PyTorch. Este documento descreve em detalhes o dataset utilizado para treinar e avaliar o modelo.


- **Nome**: RetailRocket eCommerce Dataset
- **Fonte**: Kaggle - RetailRocket
- **Descrição**: Dataset de eventos de e-commerce com comportamento de usuários, propriedades de itens e árvore de categorias
- **Período de Coleta**: 2015-05-03 03:00:04 até 2015-09-18 02:59:47
---

### como obter o dataset
```python
import kagglehub

# Download latest version
path = kagglehub.dataset_download("retailrocket/ecommerce-dataset")

print("Path to dataset files:", path)
### Informações Gerais do Dataset
```
---

## 1. Arquitetura do Dataset

O dataset é composto por 4 arquivos principais em formato CSV:

### 1.1 Arquivos Disponíveis

- **events.csv**: Arquivo 1 do dataset
- **category_tree.csv**: Arquivo 2 do dataset
- **item_properties_part1.csv**: Arquivo 3 do dataset
- **item_properties_part2.csv**: Arquivo 4 do dataset


### 1.2 Estrutura Hierárquica

```
RetailRocket eCommerce Dataset/
├── events.csv                    # Eventos de usuários
├── category_tree.csv             # Hierarquia de categorias
├── item_properties_part1.csv     # Propriedades dos itens (parte 1)
└── item_properties_part2.csv     # Propriedades dos itens (parte 2)
```

---

## 2. Tabela de Eventos (events.csv)

### 2.1 Dimensões

- **Total de Registros**: 2,756,101
- **Número de Colunas**: 5
- **Usuários Únicos**: 1,407,580
- **Itens Únicos**: 235,061

### 2.2 Período de Coleta

- **Data de Início**: 2015-05-03 03:00:04
- **Data de Término**: 2015-09-18 02:59:47

### 2.3 Colunas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| timestamp | bigint | Timestamp do evento em milissegundos (Unix epoch) |
| visitorid | integer | Identificador único do visitante/usuário |
| event | string | Tipo de evento registrado |
| itemid | integer | Identificador do item relacionado ao evento |
| transactionid | integer | Identificador da transação (apenas para eventos de compra) |

### 2.4 Tipos de Eventos

- **view**: 2,664,312 (96.67%)
- **addtocart**: 69,332 (2.52%)
- **transaction**: 22,457 (0.81%)


### 2.5 Estatísticas por Evento

#### Visualizações (View)
- **Total de Visualizações**: 2,664,312
- **Usuários que Visualizaram**: 1,404,179

#### Adições ao Carrinho (Add to Cart)
- **Total de Adições**: 69,332
- **Usuários que Adicionaram**: 37,722

#### Compras (Transaction)
- **Total de Compras**: 22,457
- **Usuários que Compraram**: 11,719

### 2.6 Insights de Comportamento

- **Taxa de Conversão (View → Compra)**: 0.84%
- **Itens Mais Populares**: Os 10 itens mais visualizados

### 2.7 Estatísticas Descritivas

#### Eventos por Dia
- **Média**: 19828.1
- **Mediana**: 20621.0
- **Mínimo**: 1528
- **Máximo**: 32703

#### Eventos por Usuário
- **Média**: 2.0
- **Mediana**: 1.0
- **Mínimo**: 1
- **Máximo**: 7757
- **Percentil 90**: 3.0

#### Eventos por Item
- **Média**: 11.7
- **Mediana**: 3.0
- **Mínimo**: 1
- **Máximo**: 3412

---

## 3. Árvore de Categorias (category_tree.csv)

### 3.1 Dimensões

- **Total de Categorias**: 1669
- **Categorias Principais (Root)**: 25
- **Categorias com Hierarquia**: 1644

### 3.2 Colunas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| categoryid | integer | Identificador único da categoria |
| parentid | integer | Identificador da categoria pai (NULL para categorias raiz) |

### 3.3 Estrutura Hierárquica

- A tabela implementa uma estrutura de **árvore adjacente**, onde cada categoria pode ter uma categoria pai
- As categorias raiz são identificadas com `parentid = NULL` (ou NaN)
- Permite criar taxonomias de produtos multi-nível (ex: Eletrônicos → Telefones → Smartphones)

---

## 4. Propriedades dos Itens

### 4.1 Dimensões

- **Total de Registros de Propriedades**: 20,275,902
- **Itens Únicos com Propriedades**: 417,053
- **Propriedades Distintas**: 1104

### 4.2 Colunas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| itemid | integer | Identificador do item |
| property | string | Nome da propriedade/atributo |
| value | string | Valor da propriedade |

### 4.3 Tipos de Propriedades

As propriedades dos itens descrevem características e atributos dos produtos:

- **888**: 3,000,398 registros
- **790**: 1,790,516 registros
- **available**: 1,503,639 registros
- **categoryid**: 788,214 registros
- **6**: 631,471 registros
- **283**: 597,419 registros
- **776**: 574,220 registros
- **678**: 481,966 registros
- **364**: 476,486 registros
- **202**: 448,938 registros
- **839**: 417,239 registros
- **917**: 417,227 registros
- **764**: 417,053 registros
- **159**: 417,053 registros
- **112**: 417,053 registros
- **227**: 347,492 registros
- **698**: 289,849 registros
- **451**: 264,416 registros
- **663**: 240,813 registros
- **962**: 239,372 registros
- **400**: 216,481 registros
- **689**: 214,225 registros
- **28**: 172,393 registros
- **928**: 160,818 registros
- **1036**: 146,246 registros
- **810**: 142,575 registros
- **348**: 113,303 registros
- **544**: 113,246 registros
- **713**: 104,931 registros
- **1032**: 82,805 registros
- **19**: 75,744 registros
- **566**: 72,966 registros
- **581**: 68,009 registros
- **978**: 64,569 registros
- **981**: 62,513 registros
- **720**: 55,349 registros
- **243**: 54,216 registros
- **960**: 54,141 registros
- **46**: 54,141 registros
- **38**: 54,141 registros
- **434**: 54,141 registros
- **71**: 52,620 registros
- **797**: 51,271 registros
- **591**: 50,640 registros
- **961**: 49,627 registros
- **441**: 49,187 registros
- **486**: 48,335 registros
- **225**: 48,277 registros
- **575**: 47,613 registros
- **915**: 46,572 registros
- **230**: 43,687 registros
- **496**: 43,515 registros
- **188**: 41,925 registros
- **0**: 41,406 registros
- **42**: 40,336 registros
- **719**: 39,645 registros
- **550**: 39,120 registros
- **558**: 38,577 registros
- **490**: 37,100 registros
- **521**: 35,806 registros
- **686**: 35,451 registros
- **104**: 35,431 registros
- **1066**: 35,111 registros
- **761**: 34,991 registros
- **480**: 34,326 registros
- **765**: 32,778 registros
- **369**: 32,513 registros
- **61**: 31,671 registros
- **681**: 30,915 registros
- **33**: 30,883 registros
- **619**: 29,884 registros
- **213**: 29,041 registros
- **546**: 28,989 registros
- **846**: 28,731 registros
- **935**: 28,579 registros
- **102**: 28,435 registros
- **758**: 27,865 registros
- **964**: 27,658 registros
- **335**: 27,009 registros
- **186**: 26,834 registros
- **452**: 26,647 registros
- **976**: 26,336 registros
- **478**: 26,302 registros
- **830**: 26,033 registros
- **785**: 25,393 registros
- **468**: 25,317 registros
- **807**: 24,285 registros
- **235**: 23,580 registros
- **120**: 23,138 registros
- **941**: 23,113 registros
- **763**: 23,111 registros
- **921**: 22,221 registros
- **1090**: 22,174 registros
- **107**: 21,793 registros
- **506**: 21,496 registros
- **784**: 20,948 registros
- **1054**: 20,535 registros
- **588**: 20,500 registros
- **696**: 20,445 registros
- **620**: 20,334 registros
- **501**: 20,094 registros
- **956**: 20,094 registros
- **101**: 20,094 registros
- **354**: 20,094 registros
- **852**: 20,094 registros
- **529**: 19,899 registros
- **49**: 19,887 registros
- **447**: 19,823 registros
- **204**: 19,712 registros
- **931**: 19,181 registros
- **771**: 18,862 registros
- **570**: 17,776 registros
- **653**: 17,429 registros
- **595**: 17,414 registros
- **415**: 17,362 registros
- **751**: 17,258 registros
- **398**: 17,018 registros
- **993**: 16,752 registros
- **561**: 16,752 registros
- **631**: 16,441 registros
- **994**: 16,417 registros
- **602**: 16,292 registros
- **671**: 15,998 registros
- **189**: 15,365 registros
- **701**: 14,851 registros
- **709**: 14,434 registros
- **675**: 14,152 registros
- **456**: 13,977 registros
- **208**: 13,361 registros
- **815**: 13,239 registros
- **470**: 13,158 registros
- **813**: 13,118 registros
- **704**: 12,950 registros
- **438**: 12,708 registros
- **83**: 12,574 registros
- **658**: 12,168 registros
- **30**: 12,118 registros
- **611**: 12,092 registros
- **119**: 11,879 registros
- **1081**: 11,829 registros
- **614**: 11,765 registros
- **753**: 11,536 registros
- **837**: 11,502 registros
- **96**: 11,453 registros
- **405**: 11,366 registros
- **867**: 11,247 registros
- **293**: 11,247 registros
- **628**: 11,247 registros
- **847**: 11,247 registros
- **584**: 11,247 registros
- **553**: 11,244 registros
- **646**: 11,244 registros
- **74**: 11,243 registros
- **637**: 11,243 registros
- **654**: 11,095 registros
- **464**: 10,701 registros
- **332**: 10,593 registros
- **624**: 10,562 registros
- **881**: 10,562 registros
- **685**: 10,562 registros
- **1014**: 10,562 registros
- **47**: 10,562 registros
- **277**: 10,481 registros
- **1031**: 10,481 registros
- **35**: 10,104 registros
- **410**: 9,895 registros
- **325**: 9,587 registros
- **1028**: 9,559 registros
- **275**: 9,543 registros
- **124**: 9,540 registros
- **982**: 9,514 registros
- **892**: 9,485 registros
- **264**: 9,256 registros
- **231**: 9,082 registros
- **580**: 9,082 registros
- **988**: 9,082 registros
- **1037**: 9,082 registros
- **408**: 9,082 registros
- **355**: 9,082 registros
- **809**: 9,077 registros
- **914**: 9,049 registros
- **422**: 9,045 registros
- **1079**: 9,042 registros
- **899**: 8,896 registros
- **942**: 8,842 registros
- **1092**: 8,813 registros
- **461**: 8,302 registros
- **62**: 8,129 registros
- **955**: 8,128 registros
- **630**: 8,079 registros
- **638**: 7,906 registros
- **161**: 7,877 registros
- **908**: 7,843 registros
- **314**: 7,751 registros
- **900**: 7,734 registros
- **108**: 7,728 registros
- **460**: 7,302 registros
- **1095**: 7,231 registros
- **987**: 7,211 registros
- **509**: 7,186 registros
- **313**: 7,163 registros
- **503**: 7,120 registros
- **246**: 7,118 registros
- **543**: 7,108 registros
- **884**: 6,926 registros
- **536**: 6,842 registros
- **842**: 6,627 registros
- **491**: 6,567 registros
- **322**: 6,536 registros
- **8**: 6,496 registros
- **841**: 6,394 registros
- **515**: 6,385 registros
- **794**: 6,355 registros
- **606**: 6,328 registros
- **648**: 6,324 registros
- **176**: 6,319 registros
- **66**: 6,319 registros
- **141**: 6,319 registros
- **406**: 6,319 registros
- **278**: 6,319 registros
- **939**: 6,319 registros
- **585**: 6,319 registros
- **747**: 6,319 registros
- **297**: 6,319 registros
- **707**: 6,319 registros
- **142**: 6,319 registros
- **974**: 6,319 registros
- **122**: 6,319 registros
- **545**: 6,319 registros
- **854**: 6,319 registros
- **851**: 6,319 registros
- **898**: 6,319 registros
- **726**: 6,246 registros
- **636**: 6,225 registros
- **783**: 6,196 registros
- **113**: 6,104 registros
- **139**: 6,039 registros
- **969**: 6,001 registros
- **294**: 5,968 registros
- **1058**: 5,944 registros
- **953**: 5,941 registros
- **792**: 5,935 registros
- **15**: 5,841 registros
- **392**: 5,827 registros
- **523**: 5,816 registros
- **378**: 5,814 registros
- **397**: 5,721 registros
- **1080**: 5,708 registros
- **920**: 5,649 registros
- **819**: 5,649 registros
- **1**: 5,649 registros
- **775**: 5,630 registros
- **1041**: 5,607 registros
- **9**: 5,597 registros
- **457**: 5,551 registros
- **1057**: 5,526 registros
- **642**: 5,499 registros
- **469**: 5,498 registros
- **281**: 5,498 registros
- **60**: 5,447 registros
- **270**: 5,323 registros
- **617**: 5,284 registros
- **327**: 5,173 registros
- **586**: 5,153 registros
- **127**: 5,142 registros
- **54**: 5,138 registros
- **957**: 5,123 registros
- **932**: 5,123 registros
- **59**: 5,067 registros
- **307**: 5,016 registros
- **1075**: 4,955 registros
- **728**: 4,924 registros
- **693**: 4,885 registros
- **992**: 4,884 registros
- **222**: 4,868 registros
- **1064**: 4,792 registros
- **736**: 4,783 registros
- **431**: 4,769 registros
- **334**: 4,687 registros
- **25**: 4,667 registros
- **93**: 4,662 registros
- **710**: 4,587 registros
- **98**: 4,492 registros
- **551**: 4,483 registros
- **384**: 4,433 registros
- **745**: 4,371 registros
- **676**: 4,356 registros
- **346**: 4,356 registros
- **569**: 4,356 registros
- **344**: 4,352 registros
- **1008**: 4,316 registros
- **140**: 4,316 registros
- **284**: 4,267 registros
- **411**: 4,247 registros
- **185**: 4,236 registros
- **238**: 4,220 registros
- **296**: 4,220 registros
- **280**: 4,220 registros
- **768**: 4,215 registros
- **730**: 4,214 registros
- **40**: 4,170 registros
- **997**: 4,141 registros
- **1025**: 4,130 registros
- **300**: 4,099 registros
- **1004**: 4,054 registros
- **1051**: 3,960 registros
- **980**: 3,892 registros
- **645**: 3,745 registros
- **11**: 3,740 registros
- **594**: 3,738 registros
- **805**: 3,697 registros
- **1056**: 3,694 registros
- **869**: 3,678 registros
- **814**: 3,668 registros
- **495**: 3,663 registros
- **343**: 3,663 registros
- **621**: 3,653 registros
- **897**: 3,633 registros
- **936**: 3,631 registros
- **114**: 3,629 registros
- **795**: 3,628 registros
- **1097**: 3,601 registros
- **510**: 3,541 registros
- **680**: 3,541 registros
- **375**: 3,527 registros
- **513**: 3,520 registros
- **893**: 3,421 registros
- **279**: 3,378 registros
- **152**: 3,366 registros
- **945**: 3,353 registros
- **22**: 3,353 registros
- **796**: 3,353 registros
- **290**: 3,353 registros
- **748**: 3,353 registros
- **258**: 3,353 registros
- **215**: 3,353 registros
- **716**: 3,353 registros
- **971**: 3,353 registros
- **563**: 3,353 registros
- **589**: 3,352 registros
- **966**: 3,342 registros
- **660**: 3,226 registros
- **505**: 3,210 registros
- **605**: 3,195 registros
- **89**: 3,195 registros
- **311**: 3,195 registros
- **659**: 3,195 registros
- **1048**: 3,195 registros
- **99**: 3,195 registros
- **446**: 3,195 registros
- **207**: 3,195 registros
- **697**: 3,195 registros
- **705**: 3,195 registros
- **430**: 3,195 registros
- **286**: 3,195 registros
- **905**: 3,195 registros
- **302**: 3,195 registros
- **640**: 3,195 registros
- **1044**: 3,193 registros
- **192**: 3,193 registros
- **458**: 3,151 registros
- **210**: 3,131 registros
- **214**: 3,115 registros
- **600**: 3,090 registros
- **664**: 3,052 registros
- **1050**: 3,015 registros
- **910**: 3,007 registros
- **65**: 2,974 registros
- **665**: 2,949 registros
- **1009**: 2,934 registros
- **977**: 2,934 registros
- **879**: 2,932 registros
- **382**: 2,921 registros
- **177**: 2,919 registros
- **36**: 2,906 registros
- **12**: 2,903 registros
- **1000**: 2,853 registros
- **45**: 2,830 registros
- **727**: 2,820 registros
- **540**: 2,803 registros
- **105**: 2,781 registros
- **803**: 2,772 registros
- **423**: 2,771 registros
- **985**: 2,758 registros
- **253**: 2,757 registros
- **938**: 2,757 registros
- **324**: 2,755 registros
- **835**: 2,754 registros
- **714**: 2,749 registros
- **695**: 2,748 registros
- **684**: 2,738 registros
- **887**: 2,656 registros
- **181**: 2,642 registros
- **679**: 2,618 registros
- **178**: 2,606 registros
- **76**: 2,606 registros
- **409**: 2,574 registros
- **549**: 2,565 registros
- **862**: 2,558 registros
- **708**: 2,546 registros
- **729**: 2,514 registros
- **806**: 2,502 registros
- **669**: 2,502 registros
- **175**: 2,502 registros
- **804**: 2,502 registros
- **224**: 2,502 registros
- **233**: 2,439 registros
- **542**: 2,420 registros
- **735**: 2,380 registros
- **934**: 2,366 registros
- **592**: 2,333 registros
- **749**: 2,310 registros
- **925**: 2,283 registros
- **379**: 2,235 registros
- **259**: 2,185 registros
- **328**: 2,142 registros
- **518**: 2,127 registros
- **349**: 2,034 registros
- **418**: 2,030 registros
- **228**: 2,022 registros
- **197**: 2,010 registros
- **740**: 1,991 registros
- **69**: 1,991 registros
- **417**: 1,991 registros
- **198**: 1,991 registros
- **674**: 1,989 registros
- **479**: 1,959 registros
- **1052**: 1,937 registros
- **1068**: 1,937 registros
- **465**: 1,879 registros
- **767**: 1,833 registros
- **972**: 1,825 registros
- **652**: 1,786 registros
- **87**: 1,760 registros
- **1074**: 1,758 registros
- **1006**: 1,747 registros
- **833**: 1,729 registros
- **603**: 1,724 registros
- **16**: 1,706 registros
- **362**: 1,699 registros
- **450**: 1,669 registros
- **134**: 1,618 registros
- **80**: 1,599 registros
- **52**: 1,599 registros
- **895**: 1,599 registros
- **123**: 1,594 registros
- **389**: 1,575 registros
- **949**: 1,552 registros
- **144**: 1,545 registros
- **548**: 1,541 registros
- **780**: 1,527 registros
- **759**: 1,527 registros
- **316**: 1,527 registros
- **219**: 1,527 registros
- **151**: 1,527 registros
- **1034**: 1,527 registros
- **256**: 1,527 registros
- **265**: 1,526 registros
- **339**: 1,514 registros
- **273**: 1,493 registros
- **372**: 1,488 registros
- **587**: 1,481 registros
- **487**: 1,461 registros
- **404**: 1,461 registros
- **306**: 1,460 registros
- **822**: 1,457 registros
- **439**: 1,449 registros
- **242**: 1,449 registros
- **1093**: 1,449 registros
- **752**: 1,446 registros
- **453**: 1,436 registros
- **160**: 1,433 registros
- **1059**: 1,428 registros
- **773**: 1,420 registros
- **560**: 1,420 registros
- **547**: 1,400 registros
- **1073**: 1,358 registros
- **829**: 1,356 registros
- **562**: 1,348 registros
- **1021**: 1,335 registros
- **206**: 1,330 registros
- **448**: 1,327 registros
- **333**: 1,324 registros
- **492**: 1,319 registros
- **173**: 1,311 registros
- **13**: 1,308 registros
- **802**: 1,231 registros
- **466**: 1,210 registros
- **725**: 1,209 registros
- **271**: 1,208 registros
- **743**: 1,187 registros
- **1084**: 1,186 registros
- **475**: 1,178 registros
- **459**: 1,161 registros
- **90**: 1,159 registros
- **329**: 1,155 registros
- **853**: 1,153 registros
- **94**: 1,149 registros
- **922**: 1,149 registros
- **373**: 1,148 registros
- **538**: 1,142 registros
- **607**: 1,142 registros
- **944**: 1,110 registros
- **991**: 1,100 registros
- **413**: 1,096 registros
- **1012**: 1,082 registros
- **347**: 1,082 registros
- **746**: 1,082 registros
- **1022**: 1,082 registros
- **292**: 1,080 registros
- **1094**: 1,071 registros
- **199**: 1,070 registros
- **951**: 1,070 registros
- **268**: 1,049 registros
- **1001**: 1,047 registros
- **865**: 1,043 registros
- **454**: 1,035 registros
- **1086**: 991 registros
- **419**: 991 registros
- **831**: 991 registros
- **305**: 991 registros
- **109**: 991 registros
- **894**: 991 registros
- **50**: 991 registros
- **338**: 990 registros
- **1096**: 988 registros
- **481**: 977 registros
- **319**: 973 registros
- **578**: 970 registros
- **734**: 969 registros
- **524**: 967 registros
- **250**: 964 registros
- **153**: 960 registros
- **445**: 958 registros
- **493**: 946 registros
- **649**: 946 registros
- **788**: 946 registros
- **77**: 946 registros
- **29**: 945 registros
- **786**: 933 registros
- **996**: 931 registros
- **1017**: 920 registros
- **323**: 918 registros
- **573**: 911 registros
- **889**: 911 registros
- **723**: 911 registros
- **639**: 911 registros
- **407**: 905 registros
- **774**: 905 registros
- **880**: 887 registros
- **604**: 882 registros
- **326**: 882 registros
- **1013**: 879 registros
- **116**: 870 registros
- **32**: 870 registros
- **789**: 870 registros
- **811**: 870 registros
- **221**: 862 registros
- **863**: 859 registros
- **647**: 855 registros
- **168**: 834 registros
- **249**: 834 registros
- **903**: 834 registros
- **26**: 834 registros
- **688**: 809 registros
- **340**: 795 registros
- **866**: 776 registros
- **1060**: 772 registros
- **929**: 760 registros
- **84**: 760 registros
- **1077**: 755 registros
- **737**: 754 registros
- **350**: 751 registros
- **555**: 748 registros
- **320**: 745 registros
- **131**: 708 registros
- **821**: 693 registros
- **574**: 672 registros
- **1042**: 672 registros
- **916**: 663 registros
- **533**: 657 registros
- **571**: 657 registros
- **959**: 656 registros
- **23**: 656 registros
- **512**: 656 registros
- **257**: 656 registros
- **156**: 656 registros
- **72**: 656 registros
- **164**: 652 registros
- **201**: 641 registros
- **655**: 624 registros
- **165**: 607 registros
- **868**: 607 registros
- **115**: 603 registros
- **484**: 602 registros
- **262**: 597 registros
- **500**: 597 registros
- **299**: 594 registros
- **432**: 591 registros
- **526**: 591 registros
- **1038**: 578 registros
- **420**: 568 registros
- **618**: 567 registros
- **998**: 565 registros
- **376**: 565 registros
- **828**: 564 registros
- **483**: 561 registros
- **622**: 558 registros
- **1053**: 555 registros
- **1067**: 554 registros
- **554**: 554 registros
- **808**: 554 registros
- **909**: 550 registros
- **739**: 545 registros
- **732**: 544 registros
- **216**: 541 registros
- **223**: 535 registros
- **402**: 534 registros
- **625**: 522 registros
- **68**: 522 registros
- **608**: 522 registros
- **298**: 522 registros
- **118**: 522 registros
- **163**: 522 registros
- **731**: 520 registros
- **927**: 515 registros
- **295**: 503 registros
- **1078**: 501 registros
- **1083**: 501 registros
- **51**: 501 registros
- **64**: 500 registros
- **717**: 500 registros
- **755**: 500 registros
- **858**: 492 registros
- **613**: 492 registros
- **86**: 492 registros
- **891**: 492 registros
- **766**: 492 registros
- **1070**: 491 registros
- **597**: 491 registros
- **143**: 491 registros
- **818**: 491 registros
- **947**: 491 registros
- **901**: 491 registros
- **88**: 491 registros
- **356**: 491 registros
- **401**: 491 registros
- **948**: 491 registros
- **317**: 491 registros
- **14**: 491 registros
- **1007**: 491 registros
- **429**: 491 registros
- **583**: 491 registros
- **125**: 491 registros
- **904**: 491 registros
- **541**: 489 registros
- **121**: 487 registros
- **155**: 486 registros
- **455**: 486 registros
- **911**: 485 registros
- **644**: 481 registros
- **237**: 480 registros
- **10**: 468 registros
- **902**: 466 registros
- **196**: 466 registros
- **70**: 466 registros
- **179**: 466 registros
- **690**: 466 registros
- **517**: 466 registros
- **754**: 466 registros
- **873**: 464 registros
- **661**: 463 registros
- **845**: 462 registros
- **848**: 454 registros
- **635**: 454 registros
- **73**: 448 registros
- **220**: 447 registros
- **193**: 443 registros
- **1043**: 441 registros
- **1055**: 439 registros
- **656**: 439 registros
- **387**: 439 registros
- **1033**: 439 registros
- **668**: 439 registros
- **291**: 439 registros
- **826**: 439 registros
- **610**: 439 registros
- **149**: 439 registros
- **1098**: 439 registros
- **793**: 434 registros
- **672**: 428 registros
- **906**: 414 registros
- **687**: 414 registros
- **421**: 412 registros
- **912**: 405 registros
- **336**: 404 registros
- **777**: 400 registros
- **390**: 398 registros
- **612**: 390 registros
- **251**: 388 registros
- **194**: 386 registros
- **234**: 384 registros
- **504**: 378 registros
- **111**: 375 registros
- **738**: 375 registros
- **844**: 374 registros
- **552**: 374 registros
- **711**: 369 registros
- **756**: 369 registros
- **876**: 369 registros
- **706**: 369 registros
- **886**: 369 registros
- **341**: 369 registros
- **128**: 369 registros
- **896**: 369 registros
- **365**: 368 registros
- **973**: 365 registros
- **386**: 358 registros
- **772**: 349 registros
- **1016**: 347 registros
- **359**: 347 registros
- **135**: 345 registros
- **393**: 345 registros
- **444**: 336 registros
- **463**: 336 registros
- **245**: 335 registros
- **467**: 325 registros
- **1045**: 322 registros
- **442**: 322 registros
- **396**: 322 registros
- **832**: 318 registros
- **694**: 318 registros
- **827**: 315 registros
- **342**: 314 registros
- **154**: 309 registros
- **508**: 305 registros
- **965**: 305 registros
- **435**: 305 registros
- **952**: 305 registros
- **824**: 305 registros
- **79**: 300 registros
- **907**: 295 registros
- **520**: 293 registros
- **559**: 289 registros
- **254**: 289 registros
- **1011**: 289 registros
- **217**: 289 registros
- **1015**: 289 registros
- **361**: 289 registros
- **436**: 289 registros
- **370**: 287 registros
- **184**: 285 registros
- **781**: 281 registros
- **742**: 281 registros
- **377**: 277 registros
- **385**: 271 registros
- **240**: 264 registros
- **130**: 264 registros
- **933**: 263 registros
- **787**: 257 registros
- **100**: 253 registros
- **975**: 251 registros
- **138**: 250 registros
- **41**: 249 registros
- **117**: 248 registros
- **657**: 245 registros
- **48**: 245 registros
- **989**: 244 registros
- **984**: 244 registros
- **2**: 240 registros
- **236**: 240 registros
- **331**: 239 registros
- **979**: 234 registros
- **924**: 230 registros
- **651**: 229 registros
- **1002**: 229 registros
- **1102**: 227 registros
- **878**: 227 registros
- **963**: 225 registros
- **211**: 225 registros
- **499**: 224 registros
- **1003**: 224 registros
- **289**: 223 registros
- **37**: 221 registros
- **137**: 220 registros
- **403**: 217 registros
- **999**: 217 registros
- **860**: 216 registros
- **85**: 212 registros
- **1101**: 206 registros
- **1026**: 205 registros
- **97**: 203 registros
- **1104**: 203 registros
- **875**: 202 registros
- **252**: 202 registros
- **34**: 202 registros
- **1010**: 202 registros
- **798**: 200 registros
- **715**: 199 registros
- **103**: 198 registros
- **162**: 191 registros
- **1099**: 190 registros
- **1029**: 190 registros
- **212**: 189 registros
- **817**: 185 registros
- **416**: 184 registros
- **1071**: 182 registros
- **623**: 181 registros
- **169**: 179 registros
- **482**: 178 registros
- **337**: 176 registros
- **308**: 176 registros
- **913**: 176 registros
- **724**: 175 registros
- **593**: 173 registros
- **850**: 173 registros
- **7**: 172 registros
- **643**: 172 registros
- **683**: 171 registros
- **360**: 171 registros
- **629**: 169 registros
- **31**: 167 registros
- **315**: 166 registros
- **937**: 166 registros
- **133**: 164 registros
- **477**: 164 registros
- **800**: 162 registros
- **366**: 161 registros
- **857**: 161 registros
- **825**: 159 registros
- **287**: 158 registros
- **63**: 156 registros
- **473**: 153 registros
- **596**: 151 registros
- **943**: 150 registros
- **627**: 149 registros
- **1035**: 145 registros
- **195**: 145 registros
- **5**: 143 registros
- **849**: 142 registros
- **1087**: 140 registros
- **352**: 140 registros
- **1040**: 140 registros
- **321**: 139 registros
- **699**: 137 registros
- **801**: 137 registros
- **351**: 137 registros
- **677**: 136 registros
- **255**: 135 registros
- **539**: 135 registros
- **919**: 130 registros
- **203**: 130 registros
- **535**: 130 registros
- **930**: 129 registros
- **1047**: 128 registros
- **476**: 128 registros
- **3**: 127 registros
- **1103**: 127 registros
- **157**: 126 registros
- **170**: 123 registros
- **762**: 122 registros
- **367**: 122 registros
- **110**: 122 registros
- **519**: 115 registros
- **363**: 114 registros
- **106**: 114 registros
- **318**: 112 registros
- **779**: 110 registros
- **1065**: 109 registros
- **191**: 109 registros
- **269**: 108 registros
- **702**: 108 registros
- **577**: 108 registros
- **247**: 108 registros
- **958**: 108 registros
- **673**: 108 registros
- **282**: 107 registros
- **172**: 107 registros
- **856**: 107 registros
- **641**: 106 registros
- **209**: 106 registros
- **443**: 104 registros
- **462**: 103 registros
- **399**: 102 registros
- **823**: 102 registros
- **1061**: 102 registros
- **267**: 101 registros
- **95**: 101 registros
- **662**: 101 registros
- **1024**: 101 registros
- **171**: 100 registros
- **834**: 98 registros
- **145**: 97 registros
- **53**: 96 registros
- **380**: 96 registros
- **260**: 96 registros
- **572**: 96 registros
- **527**: 94 registros
- **136**: 94 registros
- **859**: 94 registros
- **132**: 94 registros
- **75**: 93 registros
- **950**: 92 registros
- **861**: 90 registros
- **497**: 89 registros
- **778**: 89 registros
- **609**: 88 registros
- **567**: 88 registros
- **383**: 88 registros
- **92**: 87 registros
- **20**: 86 registros
- **274**: 86 registros
- **374**: 85 registros
- **381**: 84 registros
- **836**: 83 registros
- **91**: 83 registros
- **890**: 83 registros
- **330**: 83 registros
- **205**: 83 registros
- **733**: 83 registros
- **190**: 83 registros
- **691**: 83 registros
- **882**: 83 registros
- **874**: 83 registros
- **81**: 83 registros
- **488**: 83 registros
- **1062**: 80 registros
- **986**: 79 registros
- **241**: 77 registros
- **395**: 77 registros
- **750**: 77 registros
- **568**: 77 registros
- **158**: 77 registros
- **667**: 77 registros
- **24**: 76 registros
- **599**: 75 registros
- **17**: 75 registros
- **148**: 75 registros
- **489**: 73 registros
- **126**: 73 registros
- **970**: 72 registros
- **650**: 70 registros
- **502**: 69 registros
- **433**: 69 registros
- **39**: 68 registros
- **871**: 68 registros
- **576**: 68 registros
- **760**: 67 registros
- **534**: 63 registros
- **1063**: 62 registros
- **557**: 62 registros
- **358**: 62 registros
- **1019**: 62 registros
- **1020**: 62 registros
- **412**: 58 registros
- **388**: 58 registros
- **150**: 57 registros
- **995**: 56 registros
- **18**: 55 registros
- **983**: 53 registros
- **414**: 53 registros
- **582**: 53 registros
- **263**: 52 registros
- **1023**: 51 registros
- **1100**: 51 registros
- **371**: 51 registros
- **877**: 50 registros
- **923**: 49 registros
- **187**: 48 registros
- **266**: 47 registros
- **870**: 47 registros
- **855**: 46 registros
- **166**: 46 registros
- **303**: 46 registros
- **345**: 44 registros
- **232**: 43 registros
- **537**: 43 registros
- **394**: 42 registros
- **514**: 42 registros
- **27**: 42 registros
- **1030**: 42 registros
- **449**: 40 registros
- **304**: 39 registros
- **579**: 39 registros
- **940**: 38 registros
- **843**: 38 registros
- **816**: 38 registros
- **632**: 37 registros
- **718**: 37 registros
- **1089**: 36 registros
- **1069**: 35 registros
- **437**: 35 registros
- **21**: 34 registros
- **147**: 34 registros
- **1085**: 33 registros
- **626**: 33 registros
- **885**: 32 registros
- **248**: 32 registros
- **309**: 32 registros
- **590**: 32 registros
- **840**: 31 registros
- **200**: 31 registros
- **272**: 30 registros
- **525**: 30 registros
- **864**: 29 registros
- **721**: 29 registros
- **564**: 28 registros
- **425**: 28 registros
- **682**: 28 registros
- **838**: 28 registros
- **239**: 28 registros
- **428**: 28 registros
- **670**: 28 registros
- **82**: 27 registros
- **146**: 26 registros
- **43**: 25 registros
- **44**: 24 registros
- **1082**: 24 registros
- **757**: 24 registros
- **183**: 23 registros
- **301**: 23 registros
- **1005**: 23 registros
- **615**: 21 registros
- **990**: 21 registros
- **616**: 20 registros
- **218**: 20 registros
- **812**: 20 registros
- **353**: 20 registros
- **67**: 19 registros
- **741**: 18 registros
- **692**: 18 registros
- **1076**: 18 registros
- **918**: 18 registros
- **55**: 18 registros
- **485**: 17 registros
- **182**: 17 registros
- **310**: 17 registros
- **440**: 17 registros
- **167**: 15 registros
- **954**: 14 registros
- **180**: 14 registros
- **666**: 14 registros
- **799**: 14 registros
- **56**: 14 registros
- **507**: 14 registros
- **601**: 14 registros
- **285**: 14 registros
- **426**: 14 registros
- **174**: 13 registros
- **820**: 13 registros
- **967**: 13 registros
- **1049**: 12 registros
- **276**: 12 registros
- **791**: 11 registros
- **229**: 10 registros
- **516**: 10 registros
- **528**: 10 registros
- **511**: 10 registros
- **129**: 10 registros
- **78**: 9 registros
- **357**: 9 registros
- **498**: 8 registros
- **368**: 8 registros
- **1072**: 8 registros
- **261**: 8 registros
- **4**: 7 registros
- **565**: 7 registros
- **926**: 7 registros
- **633**: 7 registros
- **1039**: 7 registros
- **700**: 7 registros
- **532**: 7 registros
- **770**: 6 registros
- **872**: 5 registros
- **531**: 5 registros
- **427**: 5 registros
- **391**: 5 registros
- **556**: 5 registros
- **1088**: 4 registros
- **598**: 4 registros
- **471**: 4 registros
- **883**: 3 registros
- **703**: 3 registros
- **58**: 3 registros
- **968**: 2 registros
- **1018**: 2 registros
- **712**: 2 registros
- **494**: 2 registros
- **1027**: 2 registros
- **1091**: 1 registros
- **522**: 1 registros
- **634**: 1 registros
- **424**: 1 registros
- **244**: 1 registros
- **530**: 1 registros
- **472**: 1 registros
- **722**: 1 registros
- **744**: 1 registros
- **57**: 1 registros
- **782**: 1 registros
- **288**: 1 registros
- **769**: 1 registros
- **312**: 1 registros
- **1046**: 1 registros


### 4.4 Formato dos Dados

- **Estrutura**: Dados em formato de pares chave-valor
- **Particionamento**: Dividido em 2 arquivos (part1 e part2) para facilitar gerenciamento
- **Variabilidade**: Diferentes itens podem ter conjuntos diferentes de propriedades

---

## 5. Qualidade dos Dados

### 5.1 Valores Nulos

#### events.csv
- **timestamp**: Sem valores nulos ✓
- **visitorid**: Sem valores nulos ✓
- **event**: Sem valores nulos ✓
- **itemid**: Sem valores nulos ✓
- **transactionid**: 2733644 valores nulos
- **timestamp_datetime**: Sem valores nulos ✓


#### category_tree.csv
- **categoryid**: Sem valores nulos ✓
- **parentid**: 25 valores nulos


### 5.2 Duplicatas

- **events.csv**: 460 registros duplicados

---

## 6. Casos de Uso

### 6.1 Sistema de Recomendação

O dataset é ideal para desenvolver sistemas de recomendação de produtos:

- **Filtragem Colaborativa**: Análise de preferências de usuários baseada em visualizações e compras
- **Recomendação Baseada em Conteúdo**: Uso de propriedades de itens para recomendar produtos similares
- **Ranking Personalizado**: Treino de modelos para ordenar produtos por relevância

### 6.2 Análise de Comportamento do Usuário

- **Padrões de Navegação**: Análise de caminho do usuário pela plataforma
- **Taxa de Conversão**: Medição de funil de vendas (view → add to cart → purchase)
- **Segmentação de Usuários**: Identificação de grupos com comportamentos similares

### 6.3 Otimização de Catálogo

- **Desempenho de Produtos**: Identificação de produtos populares vs. com baixo interesse
- **Gestão de Categoria**: Análise de hierarquia de categorias e reorganização
- **Atributos Relevantes**: Identificação de propriedades que influenciam a compra

---

## 7. Características Notáveis

### 7.1 Pontos Fortes

✅ **Dataset Equilibrado**: Mistura de eventos de navegação, adição ao carrinho e compras
✅ **Temporal Rich**: Timestamps precisos permitem análise de séries temporais
✅ **Estrutura Hierarchical**: Categorias organizadas em árvore permite análise de hierarquia
✅ **Atributos Descritivos**: Propriedades dos itens fornecem contexto para recomendações
✅ **Escala Real**: Milhões de eventos de usuários reais

### 7.2 Considerações

⚠️ **Esparsidade**: Nem todos os usuários têm todas as interações com todos os itens
⚠️ **Propriedades Variáveis**: Não todos os itens possuem o mesmo conjunto de propriedades
⚠️ **Data Drift**: Padrões podem variar ao longo do tempo

---

## 8. Preparação e Engenharia de Features

### 8.1 Transformações Comuns

Para uso em modelos de machine learning, recomenda-se:

1. **Normalização de Timestamp**: Converter para formato relativo ou sessão
2. **Codificação de Categorias**: One-hot encoding ou embedding para categoria_id
3. **Features de Frequência**: Contar interações por usuário, item e tipo de evento
4. **Features Temporais**: Extrair hora, dia da semana, tempo desde última interação
5. **Normalização de Propriedades**: Padronizar valores de propriedades dos itens

### 8.2 Estratégias de Validação

- **Validação Temporal**: Usar dados históricos para treinar, futuros para validar
- **Cross-validation**: Estratificação por usuário para evitar vazamento
- **Hold-out Set**: Reservar porcentagem de usuários e transações para teste final

---

## 9. Estatísticas Resumidas

| Métrica | Valor |
|---------|-------|
| Total de Eventos | 2,756,101 |
| Usuários Únicos | 1,407,580 |
| Itens Únicos | 235,061 |
| Categorias | 1669 |
| Período (dias) | ~137 dias |
| Taxa de Conversão | 0.84% |

---

## 10. Referências e Metadados

- **Dataset Original**: [RetailRocket eCommerce Dataset - Kaggle](https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset)
- **Licença**: Verificar termos de uso no Kaggle
- **Descrição Completa**: Consultar página do dataset para background técnico
- **Tamanho Total**: Múltiplos GB após completo carregamento

---

**Documento Gerado**: 2026-05-31 12:54:39
**Versão**: 1.0
**Dataset Version**: 2 (Kaggle kagglehub)

---

## Notas Finais

Este dataset é altamente recomendado para:
- Pesquisa em sistemas de recomendação
- Estudos de análise de comportamento do consumidor
- Desenvolvimento de pipelines ETL e modelos de ML
- Prototipos de plataformas de e-commerce

Para questões específicas sobre os dados, consulte a documentação oficial no Kaggle.
