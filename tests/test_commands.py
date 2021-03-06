# ----------------------------------------------------------------------------
# Copyright (c) 2015--, platypus development team.
#
# Distributed under the terms of the GPL License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from os.path import join, dirname, abspath
from shutil import rmtree
from tempfile import gettempdir
from unittest import TestCase, main
from click import BadParameter

from platypus.commands import split_db, compare


class TestSplitDB(TestCase):
    def setUp(self):
        self.base = abspath(join(dirname(__file__), 'support_files'))
        self.tax_fp = join(self.base, 'small-bacteria.contigs.txt')
        self.seqs_fp = join(self.base, 'small-bacteria.contigs.fna')

        self.bad_tax_fp = join(self.base, 'bad-taxa.txt')
        self.bad_split_fp = join(self.base, 'bad-split.txt')

        self.to_delete = []

    def tearDown(self):
        for d in self.to_delete:
            try:
                rmtree(d)
            except OSError:
                pass

    def test_split_db(self):
        temp_dir = gettempdir()
        self.to_delete.append(temp_dir)

        split_db(self.tax_fp, self.seqs_fp, 'Streptococcus', temp_dir, None)

        exp_interest = join(self.base, 'interest.fna')
        exp_rest = join(self.base, 'rest.fna')

        out_interest = join(temp_dir, 'interest.fna')
        out_rest = join(temp_dir, 'rest.fna')

        with open(exp_interest) as exp, open(out_interest) as out:
            self.assertItemsEqual(exp.readlines(), out.readlines())

        with open(exp_rest) as exp, open(out_rest) as out:
            self.assertItemsEqual(exp.readlines(), out.readlines())

    def test_split_db_no_results(self):
        with self.assertRaises(BadParameter):
            split_db(self.tax_fp, self.seqs_fp, ":L doesn't exist", 'output',
                     None)

    def test_split_db_split_fp(self):
        temp_dir = gettempdir()
        self.to_delete.append(temp_dir)

        split_fp = join(self.base, 'split_fp.txt')

        split_db(self.tax_fp, self.seqs_fp, None, temp_dir, split_fp)

        exp_interest = join(self.base, 'split-interest.fna')
        exp_rest = join(self.base, 'split-rest.fna')

        out_interest = join(temp_dir, 'interest.fna')
        out_rest = join(temp_dir, 'rest.fna')

        with open(exp_interest) as exp, open(out_interest) as out:
            self.assertItemsEqual(exp.readlines(), out.readlines())

        with open(exp_rest) as exp, open(out_rest) as out:
            self.assertItemsEqual(exp.readlines(), out.readlines())

    def test_split_db_split_fp_errors(self):
        temp_dir = gettempdir()
        self.to_delete.append(temp_dir)

        with self.assertRaises(BadParameter):
            split_db(self.bad_tax_fp, self.seqs_fp, 'Streptococcus', temp_dir,
                     None)

        with self.assertRaises(BadParameter):
            split_db(self.tax_fp, self.seqs_fp, None, temp_dir,
                     self.bad_split_fp)


class TestCompare(TestCase):
    def setUp(self):
        self.base = abspath(join(dirname(__file__), 'support_files'))
        self.interest_fp = join(self.base, 'first_db.txt')
        self.other_fp = join(self.base, 'second_db.txt')

        self.to_delete = []

    def tearDown(self):
        for d in self.to_delete:
            try:
                rmtree(d)
            except OSError:
                pass

    def test_compare_base(self):
        temp_dir = gettempdir()
        self.to_delete.append(temp_dir)

        compare(self.interest_fp, self.other_fp, temp_dir)

        files = ['compile_output.txt', 'compile_output_no_nohits.txt',
                 'summary_p1_70-a1_50_p2_70-a2_50.txt']
        for fp in files:
            exp_fp = join(self.base, 'compare-tests', fp)
            out_fp = join(temp_dir, fp)

            with open(exp_fp) as exp, open(out_fp) as out:
                self.assertItemsEqual(exp.readlines(), out.readlines())

    def test_compare_exceptions(self):
        temp_dir = gettempdir()
        self.to_delete.append(temp_dir)

        with self.assertRaises(BadParameter):
            compare(self.interest_fp, self.other_fp, temp_dir,
                    interest_pcts=(50, 55), other_pcts=(100,))

        with self.assertRaises(BadParameter):
            compare(self.interest_fp, self.other_fp, temp_dir,
                    interest_alg_lens=(20,), other_alg_lens=(100, 10))

    def test_hits_to_both(self):
        temp_dir = gettempdir()
        self.to_delete.append(temp_dir)

        compare(self.interest_fp, self.other_fp, temp_dir, hits_to_first=True,
                hits_to_second=True)

        files = ['compile_output.txt', 'compile_output_no_nohits.txt',
                 'hits_to_first_db_p1_70-a1_50_p2_70-a2_50.txt',
                 'hits_to_second_db_p1_70-a1_50_p2_70-a2_50.txt',
                 'summary_p1_70-a1_50_p2_70-a2_50.txt']

        for fp in files:
            exp_fp = join(self.base, 'compare-tests', fp)
            out_fp = join(temp_dir, fp)

            with open(exp_fp) as exp, open(out_fp) as out:
                self.assertItemsEqual(exp.readlines(), out.readlines())


if __name__ == '__main__':
    main()
