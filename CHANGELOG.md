CHANGE LOG
==========

#### 0.1.2 Bouncing Capybara
This is a bugfix release with several stability and performance improvements

* Multiple Enrichment Speedups:
  * Rewrite of ASN enrichment code
  ([#42](https://github.com/mlsecproject/combine/issues/42),
  [#104](https://github.com/mlsecproject/combine/issues/104))
  * Speedup of GeoIP code - thanks to [@jeffbryner](https://github.com/jeffbryner)
* Better csv-based extraction on packetmail - thanks to [@btv](https://github.com/btv)
* Exporting extracted data to CRITs ([#84](https://github.com/mlsecproject/combine/issues/84), [#91](https://github.com/mlsecproject/combine/issues/91), [#94](https://github.com/mlsecproject/combine/issues/94)) - thanks to [@paulpc](https://github.com/paulpc)
* Better Logging Facility ([#34](https://github.com/mlsecproject/combine/issues/34))
* Updated grequests and Exception Handling ([#78](https://github.com/mlsecproject/combine/issues/78),
[#32](https://github.com/mlsecproject/combine/issues/32))

#### 0.1.1 Ascending Capybara
This is a bugfix release to improve the stability of "tiq-test" enriched data generation

* Enriched IP generation should work fine in this release. ([#58](https://github.com/mlsecproject/combine/issues/58), [#67](https://github.com/mlsecproject/combine/issues/67), [#76](https://github.com/mlsecproject/combine/issues/76))
* Supports simple lists of IP addresses and domain names as local file importing ([#48](https://github.com/mlsecproject/combine/issues/48))

Revision of enriched DNS data generation is on track for v0.1.2

#### 0.1 Capybara
* First release of combine, for the talks in BSidesLV 2014 and DEF CON 22.
