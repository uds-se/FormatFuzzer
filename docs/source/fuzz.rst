
.. highlight:: python

Fuzzing
========

With the addition of the :any:`pfp.fuzz` module, pfp now supports fuzzing
out-of-the box! (w00t!).

Strategies
^^^^^^^^^^

My (d0c_s4vage's) most successful fuzzing approaches have been ones that
allowed me to pre-define various fuzzing strategies. This allows one to reuse, tweak
existing, or create new strategies specific to each target or attack surface.

StratGroup
-----------

pfp strategy groups are containers for sets of field-specific fuzzing strategies.
:any:`StratGroups <pfp.fuzz.strats.StratGroup>` must define a
:any:`unique name <pfp.fuzz.strats.StratGroup.name>`. Strategy groups may also define
a custom :any:`filter_fields <pfp.fuzz.strats.StratGroup.filter_fields>` method.

E.g. To define a strategy that *only* fuzzes integers, one could do something
like this:

.. code-block:: python

    class IntegersOnly(pfp.fuzz.StratGroup):
        name = "ints_only"

        class IntStrat(pfp.fuzz.FieldStrat):
            klass = pfp.fields.IntBase
            choices = [0, 1, 2, 3]

        def filter_fields(self, fields):
            return filter(lambda x: isinstance(x, pfp.fields.IntBase), fields)

Then, after parsing some data using a template, the returned ``Dom`` instance
could be mutated like so:

.. code-block:: python

    dom = pfp.parse(....)
    for mutation in pfp.fuzz.mutate(dom, "ints_only", num=100, at_once=3):
        mutated = mutation._pfp__build()
        # do something with it

Note that the string ``ints_only`` was used as the :any:`strat_name_or_cls <pfp.fuzz.mutate>`
field. We could have also simply passed in the ``IntegersOnly`` class:

.. code-block:: python

    dom = pfp.parse(....)
    for mutation in pfp.fuzz.mutate(dom, IntegersOnly, num=100, at_once=3):
        mutated = mutation._pfp__build()
        # do something with it

FieldStrat
----------

:any:`FieldStrats <pfp.fuzz.strats.FieldStrat>` define a specific fuzzing strategy
for a specific field (or set of fields).

All :any:`FieldStrats <pfp.fuzz.strats.FieldStrat>` must have either a
:any:`choices <pfp.fuzz.strats.FieldStrat.choices>` field defined or a
:any:`prob <pfp.fuzz.strats.FieldStrat.prob>` field defined.

Alternately, the :any:`next_val <pfp.fuzz.strats.FieldStrat.next_val>` function
may also be overriden if something more specific is needed.


Fuzzing Reference Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pfp.fuzz
   :members:
.. automodule:: pfp.fuzz.strats
   :members:
.. automodule:: pfp.fuzz.basic
   :members:
