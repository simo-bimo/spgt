# SPGT: Small Plans for Good Times

A planner for Fully Observable Non-Deterministic (FOND) Planning domains with temporal goals specified in Pure-Past Linear Temporal Logic (PPLTL). This was produced as part of my Honours Thesis in Computer Science at the University of Sydney in 2025.

This planner is an extension of the [cfond-asp](https://github.com/ssardina-research/cfond-asp) planner, which adds support for goals specified in finite domain propositional logic and PPLTL. It is written largely in Answer Set Programming (ASP), and uses the [clingo](https://potassco.org/clingo/) ASP solver from the [Potassco collection](https://potassco.org/).

## Installation

There are two primary ways to install the planner. One can either use `pip` to install it directly from this repository:
```bash
pip install git+https://github.com/simo-bimo/spgt.git
# or
python3 -m pip install git+https://github.com/simo-bimo/spgt.git
```
or one can first clone the repository, and then install it with `pip`. This has the advantage of giving access to some of the sample problems, and allows package to be installed in a editable way for development:
```bash
git clone https://github.com/simo-bimo/spgt.git
cd spgt
pip install .
# or to install as an editable package for development
pip install -e .
```
In either case, the `spgt` command should then be available in the path.

## Usage

The planner requires a planning domain and problem instance file, both specified in `pddl`. The general format is:
```bash
spgt <domain-file> <instance-file> [flags]
```
To use one of the example problems present in the repository one may run
```bash
cd spgt/benchmarks/domains/
spgt acrobatics/domain.pddl acrobatics/p01.pddl
```
This will cause the planner to attempt to solve the planning problem by iteratively increasing the number of nodes. When done, there will be an `output` folder which contains two files. `instance.lp` is the translated FOND Problem in ASP. `output.lp` is the output of clingo solver.

To see a visual representation of the controller the planner calculates, one can add the `-gr` or `--graph` flags. This invokes [clingraph](https://potassco.org/clingraph/) to generate a graph of the resulting controller, stored in `output/graph_default.png`. The nodes are labelled with the actions they take. The initial node has a bold border, and the final node a double border.

There are several other flags available:

- `-td <file_name>` or `--temp_dir=<file_name>`: rename the output directory. Useful for solving many problems at once.
- `--subprocess`: invoke clingo as a subprocess rather than through the Python API. This is sometimes able to fix errors, as the CLI for clingo is more robust.
- `--clingo_path=<PATH>`: provide a path to a different ASP Solver. Note that this only takes effect if `--subprocess` is set, and that some `clingo` arguments will be passed to this solver alongside the ASP files.
- `--time_limit=x`: give up solving after `x` seconds. `x` may be a float, though it is implemented approximately as clingo only supports whole number time constraints. Forces clingo to invoke as a subprocess.
- `--start_size=n`: start iterating from `n` nodes, rather than `1`.
- `--strong`: calculate a strong, rather than a strong-cyclic, controller.
- `--ppltl`: use the PPLTL regressor and planner instead of the boolean logic one.
- `-g <formula>` or `--goal=<formula>`: used to overwrite the goal formula of the problem instance with `<formula>`.

Overwriting goals supports the following syntax:

- `(v = x)` the atomic statement that variable `v` takes value `x`. Use `trueValue` and `falseValue` to assign booleans.
- `!F` the negation of `F`.
- `(A&B)` the conjunction of `A` and `B`.
- `(A|B)` the disjunction of `A` and `B`. 
- `YA` yesterday `A`.
- `(ASB)` `A` since `B`.
- `(AZB)` the dual of `A` since `B`.

The dual of since $\mathcal{S}_\mathcal{D}$ is defined by
$$
A\ \mathcal{S}_\mathcal{D}\ B \equiv \neg(\neg A\  \mathcal{S}\ \neg B)
$$

If you are uncertain of what variables may be present in the domain after the translation process, you may invoke `-g ?`, `--goal=?`, `-g TELLME` or `--goal=TELLME` to get a print out of the variables and logic symbols available in the translated domain.

## An Example Problem
One may run:
```
# pwd = spgt/benchmarks/domains/
spgt acrobatics/domain.pddl\
 acrobatics/p03.pddl\
 --graph \
 --goal="(Y(Y(Y(Y(Y(position=p0)))))&((position=p0)S(position=p1)))&(up() = trueValue)"
```
This should produce an instance similar to [this one](examples/acrobatics_p03_ppltl/instance.lp) and an output similar to [this one](examples/acrobatics_p03_ppltl/output.lp). They may not be identical, as there are solutions to this planning problem. One possible graph output is as below:

---
![Graph of a strong-cyclic controller for a PPLTL objective in the acrobatics domain.](examples/acrobatics_p03_ppltl/graph_default.png)
---

Notice the controller walks from position `0` to `1`, then `2` and back to `1` then `0`, before climbing onto the beam. This means that five states ago (the initial node), the agent was in position `0`, and it has been in position `0` since it was last in position `1`, at the fourth node (confusingly labelled `Node 1` in our graph). Climbing up also makes `top()` true, and so we find the goal is satisfied.

We can make the goal more complicated by swapping positions `1` and `0` for some other positions. This requires the planner to climb first, `p0` is the only location with the ladder to get on the beam. Running:

```bash
spgt acrobatics/domain.pddl\
  acrobatics/p03.pddl\
  --graph\
  --goal="(Y(Y(Y(Y(Y(position=p0))))) & ((position=p4)S(position=p3)) ) & (up() = trueValue)"
```
produces the following:

![Graph of a strong-cyclic controller for a harder PPLTL objective in the acrobatics domain.](examples/acrobatics_p03_harder_ppltl/graph_default.png)

This essentially amounts to climbing up the ladder, and walking along the beam to position `4`. If at any time the agent fails, it walks back to position `0` and tries again.

## Contributors

Simon Dowd - simon@anldowd.com

## Design Choices