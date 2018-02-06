# Concha
An interactive command shell who deals with Spanish natural 
language and outer world.

## Why Concha?
Because it is a shell... and a bad word in Latin America.

Concha aims to use Spanish natural language as a programming 
language, not just because it is cool, but because Spanish is
a pretty ruled language (it is officially handled by the Real 
Academia Española, or [RAE](http://www.rae.es/).

## Which are the main goals
There are two main goals:

* There are many natural languages who can answer questions 
related to an "internal world". Concha must **interact with 
outer world**, mainly through HTTP calls in the most flexible 
way possible.
* There are plenty of chatbots who interact with your phone 
to set up an alarm or to buy things in your favorite online, 
but those are pre-trained tricks. Concha must be able to **be 
taught about new tricks**. This is not _deep learning_ but
_superficial teaching_.

## Current status
Currently Concha can:
* Be taught about new **tricks** through HTTP services, described 
in JSON format according to CoNNL Universal Dependences
* React upon action requests sent in plain Spanish **documents** 
according to stored tricks. All of them are stored as resources
for future reference and usage.
* Define **external actions** to interact ith external HTTP _GET_
and _POST_ services
* Define **internal actions** to _TREAT_ a document or part of it 
in order to do direct modifications or to recursively explore 
new approaches to the full document.
* Build unattended constructs of different tricks in a recursive 
manner to solve documents who have **dependent clauses**.
* Respond in plain Spanish **combining parts** of incoming document
or intermediate tricks output.

Current extra-bonusses:
* There's a Servers mock to play with as an external orld playground
* It was meant to be _Spanish only_, but... hat the heck! it speacks 
40 more languages as well, English included (you have to download the
proper model for the _SyntaxNet Universal Parser_).

Currently Concha has some limitations:
* It has no persistence. All tricks are forgotten once it stops.
* It is synchronous
* It calls in an extremely innefficient way to external parsers
(who runs several paralel TensorFlow models loading from scratch
every call), so response times can go far beyond 10 seconds.

Comparison to Shellscript
It is not a programming language yet. If we compare it to a
common shell script it only does:
* Prompt.
* Process execution (HTTP).
* Processes pipelining (|) joining outputs with inputs (done in
an autonomous way in this case)
* Process execution return value (following HTTP coding).

## Installation
Well, this is pretty simple. Just clone the project parallel
to TensorFlow/SyntaxNet and run `concha.py` in python3 from 
`concha/concha` execution directory.

1. Have `tensorflow/models/research/syntaxnet` installed on 
whatever X directory.
2. Follow the SyntaxNet installation instructions detailed 
[here](https://github.com/tensorflow/models/tree/master/research/syntaxnet#installation) 
3. There should be some directory structure like this: 
`X/models/research/syntaxnet/syntaxnet`.
4. Clone this very repository over X directory.
5. There should be some directory structure like this:
`X/concha/concha` and you are done.

### Credits
* Files `parse.sh` and `context.pbtx` on `concha/concha` directory 
are part of `universal-parsey` as mentioned in SyntaxNet documentation, 
but they are not included in the official repository. You can find them in `mldb.ai` organization
at [this repo](https://github.com/mldbai/tensorflow-models/tree/master/syntaxnet/syntaxnet/models/parsey_universal)
(it should be located at models/research/syntaxnet/syntaxnet/models/parsey-universal/)
* Laguage models located at `concha/lang_models` are referenced 
in the SyntaxNet [documentation](https://github.com/tensorflow/models/blob/master/research/syntaxnet/g3doc/universal.md), 
but they claim you must download them. Given they are exposed under 
the same Syntaxnet License, I've included them here for your convenience. 

## Execution
TBD curl examples

## Final goals
When we, humans, teach each other (and I'm not talking about 
learning, but teaching), we use tonnes of natural language 
piled through centuries to transfer wisdom, to tell how to do 
things, to register queryable facts... Evolution must not be 
that wrong, otherwise we should be talking in P-Code or 
Assembler. In next to come versions, Concha will:

* Be taught in plain spanish (without intermediate formal 
declaration of new tricks).
* Ask for help to other Concha instances to solve hat it has 
been asked for.
* Teach other Concha instances using Spanish.