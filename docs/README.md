# FormatFuzzer

`FormatFuzzer` is a framework for *high-efficiency, high-quality generation and parsing of binary inputs.*
It takes a *binary template* that describes the format of a binary input and generates an *executable* that produces and parses the given binary format.
From a binary template for GIF, for instance, `FormatFuzzer` produces a GIF generator - also known as *GIF fuzzer*.

Generators produced by `FormatFuzzer` are highly efficient, producing thousands of valid test inputs per second - in sharp contrast to mutation-based fuzzers, where the large majority of inputs is invalid. By default, `FormatFuzzer` operates in black-box settings, but can also integrate with AFL++ to produce valid inputs that also aim for maximum coverage.

FormatFuzzer is open source, available from the [FormatFuzzer project page](https://github.com/uds-se/FormatFuzzer). Contributors are welcome!
For details on how `FormatFuzzer` works and how it compares, read [our paper](https://arxiv.org/abs/2109.11277) for more info.



## Latest News from [@FormatFuzzer](https://twitter.com/FormatFuzzer)

<a class="twitter-timeline" data-lang="en" data-height="300" data-width="350" data-chrome="noheader nofooter noborders transparent"
href="https://twitter.com/FormatFuzzer" data-dnt="true">Tweets by FormatFuzzer</a> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 



