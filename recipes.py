#!/usr/bin/env python
# recipes.py
#
# Entry Point for Variant Filtration with Neural Nets
# The design philosophy is to have small functions in here.
# High-level descriptions to create training sets, architectures, and evaluations.
# Each function can be considered a recipe for cooking up a neural net.
# The gory details of finding data should be in training_data.py
# Model architectures and optimizations should be in models.py
#
# December 2016
# Sam Friedman 
# sam@broadinstitute.org

# Python 2/3 friendly
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# Imports
import os
import sys
import vcf
import h5py
import time
import plots
import pysam
import models
import defines
import operator
import arguments
import numpy as np
import training_data as td
from collections import Counter

def run():
	'''Dispatch on args.mode command-line supplied recipe'''
	args = arguments.parse_args()

	# Model training recipes
	if 'train_reference' == args.mode:
		make_reference_net(args)
	elif 'train_reference_annotation' == args.mode:
		make_reference_annotation_net(args)
	elif 'train_reference_plus_skip' == args.mode:
		train_reference_plus_skip(args)		
	elif 'train_reference_1layer' == args.mode:
		make_reference_annotation_net_1layer(args)		
	elif 'train_annotation_mlp' == args.mode:
		make_annotation_multilayer_perceptron(args)
	elif 'train_ref_read' == args.mode:
		train_ref_read_model(args)
	elif 'train_ref_read_resnet' == args.mode:
		train_ref_read_resnet_model(args)
	elif 'train_ref_read_dilated' == args.mode:
		train_ref_read_dilated_model(args)
	elif 'train_train_ref_read_b' == args.mode:
		train_ref_read_model_b(args)
	elif 'train_ref_read_bayes' == args.mode:
		train_ref_read_inception_model(args)
	elif 'train_pileup_filter' == args.mode:
		train_pileup_filter(args)
	elif 'train_calling_model' == args.mode:
		train_calling_model(args)
	elif 'train_calling_full2d' == args.mode:
		train_calling_model_full(args)		
	elif 'train_calling_model_1d' == args.mode:
		train_calling_model_1d(args)		
	elif 'train_ref_read_anno' == args.mode:
		train_ref_read_annotation_model(args)								
	elif 'train_ref_read_anno_exome' == args.mode:
		train_ref_read_annotation_exome_model(args)	
	elif 'train_bqsr' == args.mode:
		bqsr_train_tensor(args)
	elif 'train_bqsr_anno' == args.mode:
		bqsr_train_annotation_tensor(args)		
	elif 'train_bqsr_lstm' == args.mode:
		bqsr_lstm_train_tensor(args)								
	elif 'train_depristo_inception' == args.mode:
		depristo_inception(args)

	# Model testing recipes
	elif 'test_tensor' == args.mode:
		test_tensor_and_annotations(args)
	elif 'test_tensor_exome' == args.mode:
		test_ref_read_annotation_exome_model(args)		
	elif 'test_tensor_vcf' == args.mode:
		test_tensor_vs_vcf(args)
	elif 'test_tensor_multi_vcf' == args.mode:
		test_tensor_vs_multiple_vcfs(args)
	elif 'test_tensor_filters' == args.mode:
		test_tensor_and_annotations_vs_filters(args)		
	elif 'test_tensor_gnomad' == args.mode:
		test_tensor_vs_gnomad(args)
	elif 'test_refconv_gnomad' == args.mode:
		test_refconv_vs_gnomad(args)									
	elif 'test_refconv' == args.mode:
		test_reference_annotation_net(args)
	elif 'test_ref' == args.mode:
		test_reference_net(args)
	elif 'test_anno_mlp' == args.mode:
		test_annotation_multilayer_perceptron(args)
	elif 'test_caller' == args.mode:
		test_caller_pileup(args)
	elif 'test_caller_2d' == args.mode:
		test_caller_2d(args)
	elif 'test_architectures' == args.mode:
		test_architectures(args)

	# Plotting recipes
	elif 'plot_vcf_roc' == args.mode:
		plot_vcf_roc(args)
	elif 'plot_vcf_roc_gnomad' == args.mode:
		plot_vcf_roc_gnomad_scores(args)
	elif 'plot_vcf_roc_gnomad_like' == args.mode:
		plot_vcf_roc_gnomad_like_scores(args)		
	elif 'plot_multi_vcf_roc' == args.mode:
		plot_multi_vcf_roc(args)	
	elif 'roc_animation' == args.mode:
		roc_curve_through_learning(args)
	elif 'pr_segmentation_animation' == args.mode:
		roc_curve_through_learning_segmentation(args)

	# Writing tensor datasets for training
	elif 'write_tensors' == args.mode:
		td.tensors_from_tensor_map(args, include_annotations=True)
	elif 'write_paired_read_tensors' == args.mode:
		td.paired_read_tensors_from_map(args, include_annotations=True)
	elif 'write_tensors_2bit' == args.mode:
		td.tensors_from_tensor_map_2channel(args, include_annotations=True)
	elif 'write_tensors_no_annotations' == args.mode:
		td.tensors_from_tensor_map(args, include_annotations=False)		
	elif 'write_tensors_gnomad_annotations' == args.mode:
		td.tensors_from_tensor_map_gnomad_annos(args)
	elif 'write_tensors_gnomad_annotations_per_allele_1d' == args.mode:
		td.tensors_from_tensor_map_gnomad_annos_per_allele(args, include_reads=False, include_reference=True)
	elif 'write_tensors_gnomad_1d' == args.mode:
		td.tensors_from_tensor_map_gnomad_annos(args, include_reads=False, include_reference=True)		
	elif 'write_depristo' == args.mode:
		td.nist_samples_to_png(args)
	elif 'write_calling_tensors' == args.mode:
		td.calling_tensors_from_tensor_map(args)
	elif 'write_pileup_filter_tensors' == args.mode:
		td.tensors_from_tensor_map(args, pileup=True)		
	elif 'write_calling_tensors_1d' == args.mode:
		td.calling_tensors_from_tensor_map(args, pileup=True)		
	elif 'write_dna_tensors' == args.mode:
		td.write_dna_and_annotations(args)
	elif 'write_bed_tensors' == args.mode:
		td.write_dna_multisource_annotations(args)
	elif 'write_bed_tensors_dna' == args.mode:
		td.write_dna_multisource_annotations(args, include_annotations=False)		
	elif 'write_bed_tensors_annotations' == args.mode:
		td.write_dna_multisource_annotations(args, include_dna=False)	
	elif 'write_bqsr_tensors' == args.mode:
		td.bqsr_tensors_from_tensor_map(args, include_annotations=True)	
	elif 'write_filters_2d' == args.mode:
		model = models.build_read_tensor_2d_and_annotations_model(args)
		models.write_filters_2d(args, model)
	elif 'write_filters_1d' == args.mode:
		model = models.build_reference_model(args)
		models.write_filters_1d(args, model)
	elif 'write_tranches' == args.mode:
		td.write_tranches(args)

	# Inspections			
	elif 'inspect_tensors' == args.mode:
		td.inspect_read_tensors(args)
	elif 'inspect_dataset' == args.mode:
		td.inspect_dataset(args)
	elif 'inspect_architectures' == args.mode:
		inspect_architectures(args)
	elif 'inspect_gnomad' == args.mode:
		td.inspect_gnomad_low_ac(args)
	elif 'combine_vcfs' == args.mode:
		td.combine_vcfs(args)

	# Ooops
	else:
		print('\n\n ERROR! Unknown recipe mode:', args.mode, '\n\n\n')


def inspect_architectures(args):
	'''Run one batch of training and inference for each architecture in defines.architectures.

	Many command line arguments are ignored to give each architecture required values.
	Calls models.inspect_model() on each model for timing, etc

	Arguments:
		args.batch_size The size of the batch to time 
	'''	
	args.samples = 10
	for a in defines.architectures.keys():

		args.tensor_map = a
		args.window_size = 128
		args.labels = defines.snp_indel_labels
		args.input_symbols = defines.inputs_indel
		in_channels = defines.total_input_channels_from_args(args)
		if args.channels_last:
			tensor_shape = (args.read_limit, args.window_size, in_channels)
		else:
			tensor_shape = (in_channels, args.read_limit, args.window_size) 

		per_class_max = 300
		args.data_dir = defines.architectures[a]
		args.weights_hd5 = args.data_dir + a +'.hd5'
		train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)
		print('Inspecting architecture:', a, 'tensor shape:', tensor_shape)

		if '1d_calling' == a:
			args.labels = defines.calling_labels
			train_paths, valid_paths, test_paths = td.get_train_valid_test_paths_all(args)
			
			generate_train = td.calling_pileup_tensors_generator(args, train_paths)
			generate_valid = td.calling_pileup_tensors_generator(args, valid_paths)
			generate_test = td.calling_pileup_tensors_generator(args, test_paths)
			
			test = generate_test.next()

			model = models.build_1d_cnn_calling_segmentation_1d(args)			
		
		elif 'bqsr' == a:
			args.window_size = 11
			args.labels = defines.base_labels_binary
			args.input_symbols = defines.bqsr_tensor_channel_map()

			generate_train = td.bqsr_tensor_generator(args, train_paths)
			generate_valid = td.bqsr_tensor_generator(args, valid_paths)
			test = td.load_bqsr_tensors_from_class_dirs(args, test_paths, per_class_max)

			model = models.build_bqsr_model(args)
			plots.print_auc_per_class(model, test[0], test[1], args.labels)	
		
		elif '2d_annotations' == a:
			generate_train = td.tensor_annotation_generator(args, train_paths, tensor_shape)
			generate_valid = td.tensor_annotation_generator(args, valid_paths, tensor_shape)
			test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max)
			model = models.build_read_tensor_2d_and_annotations_model(args)
			plots.print_auc_per_class(model, [test[0], test[1]], test[2], args.labels)		

		elif '2d' == a:
			generate_train = td.tensor_generator(args, train_paths, tensor_shape)
			generate_valid = td.tensor_generator(args, valid_paths, tensor_shape)
			test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max)
			model = models.build_read_tensor_2d_model(args)
			plots.print_auc_per_class(model, test[0], test[1], args.labels)			
		
		elif '1d_annotations' == a:
			generate_train = td.dna_annotation_generator(args, train_paths)
			generate_valid = td.dna_annotation_generator(args, valid_paths)
			test = td.load_dna_annotations_positions_from_class_dirs(args, test_paths, per_class_max)
			model = models.build_reference_plus_model(args)
			plots.print_auc_per_class(model, [test[0], test[1]], test[2], args.labels)
		
		elif '1d' == a:
			generate_train = td.dna_annotation_generator(args, train_paths)
			generate_valid = td.dna_annotation_generator(args, valid_paths)
			test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max, dataset_id='reference')
			model = models.build_reference_model(args)
			plots.print_auc_per_class(model, test[0], test[1], args.labels)			
		
		elif 'mlp' == a:
			args.window_size = 0
			generate_train = td.dna_annotation_generator(args, train_paths)
			generate_valid = td.dna_annotation_generator(args, valid_paths)
			test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max, dataset_id='annotations')
			model = models.build_annotation_multilayer_perceptron(args)
			plots.print_auc_per_class(model, test[0], test[1], args.labels)			

		elif 'deep_variant' == a:
			args.read_limit = 299
			args.window_size = 299
			image_shape = (args.read_limit, args.window_size)
			generate_train = td.image_generator(args, train_paths, shape=image_shape)
			generate_valid = td.image_generator(args, valid_paths, shape=image_shape)
			test = td.load_images_from_class_dirs(args, test_paths, shape=image_shape, per_class_max=args.samples)
			model = models.inception_v3_max(args, architecture=args.weights_hd5)	
			plots.print_auc_per_class(model, test[0], test[1], args.labels)
		
		elif '2d_2bit' == a:
			print('Error 2d_2bit not implemented yet.')
		
		else:
			print('Error Unknown architecture:', a)			

		models.train_model_from_generators(args, model, generate_train, generate_valid, args.weights_hd5)
		models.inspect_model(args, model, generate_train, generate_valid)


def train_calling_model(args):
	'''Trains the variant calling as 1D segmentation CNN architecture on tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train. 

	This architecture looks at read_tensors and predicts site_labels.
	Tensors must be generated by calling td.write_calling_tensors() before this function is used.
	After training with early stopping performance curves are plotted on the test dataset.
	'''
	args.labels = defines.calling_labels
	model = models.build_2d_cnn_calling_segmentation_1d(args)

	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths_all(args)

	generate_train = td.calling_tensors_generator(args, train_paths)
	generate_valid = td.calling_tensors_generator(args, valid_paths)
	generate_test = td.calling_tensors_generator(args, test_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test_tensors = np.zeros((args.iterations*args.batch_size,) + defines.tensor_shape_from_args(args))
	test_labels = np.zeros((args.iterations*args.batch_size, args.window_size, len(args.labels)))

	for i in range(args.iterations):
		next_batch = generate_test.next()
		test_tensors[i*args.batch_size:(i+1)*args.batch_size,:,:,:] = next_batch[0][args.tensor_map]
		test_labels[i*args.batch_size:(i+1)*args.batch_size,:] = next_batch[1]

	predictions = model.predict(test_tensors)
	print('prediction shape:', predictions.shape)

	melt_shape = (predictions.shape[0]*predictions.shape[1], predictions.shape[2])
	predictions = predictions.reshape(melt_shape)
	test_truth = test_labels.reshape(melt_shape)
	print('predictions reshaped:', predictions.shape, 'np sum truth:\n', np.sum(test_truth, axis=0), '\nnp sum pred:\n', np.sum(predictions, axis=0))
		
	plots.plot_precision_recall_per_class_predictions(predictions, test_truth, args.labels, args.id)


def train_calling_model_full(args):
	'''Trains the variant calling as 1D segmentation CNN architecture on tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train. 

	This architecture looks at read_tensors and predicts site_labels.
	Tensors must be generated by calling td.write_calling_tensors() before this function is used.
	After training with early stopping performance curves are plotted on the test dataset.
	'''
	args.labels = defines.calling_labels
	model = models.build_2d_cnn_calling_segmentation_full_2d(args)

	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths_all(args)

	generate_train = td.calling_tensors_generator(args, train_paths)
	generate_valid = td.calling_tensors_generator(args, valid_paths)
	generate_test = td.calling_tensors_generator(args, test_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test_tensors = np.zeros((args.iterations*args.batch_size,) + defines.tensor_shape_from_args(args))
	test_labels = np.zeros((args.iterations*args.batch_size, args.window_size, len(args.labels)))

	for i in range(args.iterations):
		next_batch = generate_test.next()
		test_tensors[i*args.batch_size:(i+1)*args.batch_size,:,:,:] = next_batch[0][args.tensor_map]
		test_labels[i*args.batch_size:(i+1)*args.batch_size,:] = next_batch[1]

	predictions = model.predict(test_tensors)
	print('prediction shape:', predictions.shape)

	melt_shape = (predictions.shape[0]*predictions.shape[1], predictions.shape[2])
	predictions = predictions.reshape(melt_shape)
	test_truth = test_labels.reshape(melt_shape)
	print('predictions reshaped:', predictions.shape, 'np sum truth:', np.sum(test_truth, axis=0), '\nnp sum pred :', np.sum(predictions, axis=0))
		
	plots.plot_precision_recall_per_class_predictions(predictions, test_truth, args.labels, args.id)

def train_calling_model_1d(args):
	'''Trains the variant calling as 1D segmentation CNN architecture on tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train. 

	This architecture looks at read_tensors and predicts site_labels.
	Tensors must be generated by calling td.write_calling_tensors() before this function is used.
	After training with early stopping performance curves are plotted on the test dataset.
	'''
	args.labels = defines.calling_labels

	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths_all(args)

	generate_train = td.calling_pileup_tensors_generator(args, train_paths)
	generate_valid = td.calling_pileup_tensors_generator(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_1d_cnn_calling_segmentation_1d(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	args.batch_size = args.samples # hack
	generate_test = td.calling_pileup_tensors_generator(args, test_paths)
	test_batch = generate_test.next()
	predictions = model.predict(test_batch[0])
	for i in range(30):
		print('\n\n\npredictions ', i,' is:\n', np.argmax(predictions[i,:,:], axis =-1), '\n for truth labels:\n', np.argmax(test_batch[1][i,:,:], axis=-1))
	
	print('prediction shape:', predictions.shape)

	melt_shape = (predictions.shape[0]*predictions.shape[1], predictions.shape[2])
	predictions = predictions.reshape(melt_shape)
	test_truth = test_batch[1].reshape(melt_shape)
	print('prediction shape:', predictions.shape)
	print('np sum', np.sum(test_truth, axis=0), 'np sum pred:', np.sum(predictions, axis=0))
	
	pred_subset = []
	truth_subset = []
	for i in range(predictions.shape[0]):
		if test_truth[i][0] == 1 and np.argmax(predictions[i]) == 0:
			continue
		pred_subset.append(predictions[i])
		truth_subset.append(test_truth[i])

	print('np sum', np.sum(np.array(truth_subset), axis=0), 'np sum pred:', np.sum(np.array(pred_subset), axis=0))
	
	#plots.plot_roc_per_class(model, test_batch[0], test_batch[1], args.labels, title_suffix, melt=True)
	plots.plot_roc_per_class_predictions(np.array(pred_subset), np.array(truth_subset), args.labels, args.id+'_no_reference_tp')
	plots.plot_roc_per_class_predictions(predictions, test_truth, args.labels, args.id)


def train_pileup_filter(args):
	'''Trains a variant filtration CNN architecture on pileup tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train. 

	This architecture looks at pileup_tensors centered at a variant and predicts if the variant is real.
	Tensors must be generated by calling td.write_pileup_tensors() before this function is used.
	After training with early stopping ROC curves are plotted on the test dataset.
	'''

	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.pileup_tensor_generator(args, train_paths)
	generate_valid = td.pileup_tensor_generator(args, valid_paths)
	generate_test = td.pileup_tensor_generator(args, test_paths)

	test_pileups = np.zeros((args.iterations*args.batch_size, args.window_size, defines.get_reference_and_read_channels(args)))
	test_labels = np.zeros((args.iterations*args.batch_size, len(args.labels)))

	for i in range(args.iterations):
		next_batch = generate_test.next()
		test_pileups[i*args.batch_size:(i+1)*args.batch_size,:,:] = next_batch[0]['pileup_tensor']
		test_labels[i*args.batch_size:(i+1)*args.batch_size,:] = next_batch[1]

	weight_path = arguments.weight_path_from_args(args)
	
	model = models.build_pileup_filter(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)
	
	plots.plot_roc_per_class(model, test_pileups, test_labels, args.labels, args.id)



def test_caller_pileup(args):
	'''Tests the variant calling as 1D segmentation CNN architecture on tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train. 

	This architecture looks at pileup_tensors and predicts site_labels.
	Tensors must be generated by calling td.write_calling_tensors() before this function is used.
	Performance curves are plotted on the test dataset.
	'''
	args.labels = defines.calling_labels

	_, _, test_paths = td.get_train_valid_test_paths_all(args)
	generate_test = td.calling_pileup_tensors_generator(args, test_paths)

	model = models.build_1d_cnn_calling_segmentation_1d(args)

	test_pileups = np.zeros((args.iterations*args.batch_size, args.window_size, defines.get_reference_and_read_channels(args)))
	test_labels = np.zeros((args.iterations*args.batch_size, args.window_size, len(args.labels)))

	for i in range(args.iterations):
		next_batch = generate_test.next()
		test_pileups[i*args.batch_size:(i+1)*args.batch_size,:,:] = next_batch[0]['pileup_tensor']
		test_labels[i*args.batch_size:(i+1)*args.batch_size,:] = next_batch[1]

	predictions = model.predict(test_pileups)
	print('prediction shape:', predictions.shape)

	melt_shape = (predictions.shape[0]*predictions.shape[1], predictions.shape[2])
	predictions = predictions.reshape(melt_shape)
	test_truth = test_labels.reshape(melt_shape)
	print('prediction shape:', predictions.shape)
	print('np sum truth:', np.sum(test_truth, axis=0), '\nnp sum pred :', np.sum(predictions, axis=0))
	
	pred_subset = []
	truth_subset = []
	for i in range(predictions.shape[0]):
		if test_truth[i][0] == 1 and np.argmax(predictions[i]) == 0:
			continue
		pred_subset.append(predictions[i])
		truth_subset.append(test_truth[i])

	print('np sum truth:', np.sum(np.array(truth_subset), axis=0), '\nnp sum pred :', np.sum(np.array(pred_subset), axis=0))
	
	#plots.plot_roc_per_class(model, test_batch[0], test_batch[1], args.labels, title_suffix, melt=True)
	plots.plot_roc_per_class_predictions(np.array(pred_subset), np.array(truth_subset), args.labels, args.id+'_no_reference_tp')
	plots.plot_roc_per_class_predictions(predictions, test_truth, args.labels, args.id)
	plots.plot_precision_recall_per_class_predictions(predictions, test_truth, args.labels, args.id)


def test_caller_2d(args):
	'''Tests the variant calling as 1D segmentation CNN architecture on tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train. 

	This architecture looks at read_tensors and predicts site_labels.
	Tensors are generated by calling td.write_calling_tensors() before this function is used.
	Performance curves are plotted on the test dataset.
	'''
	args.labels = defines.calling_labels

	_, _, test_paths = td.get_train_valid_test_paths_all(args)
	generate_test = td.calling_tensors_generator(args, test_paths)

	model = models.build_2d_cnn_calling_segmentation_1d(args)

	test_tensors = np.zeros((args.iterations*args.batch_size,) + defines.tensor_shape_from_args(args))
	test_labels = np.zeros((args.iterations*args.batch_size, args.window_size, len(args.labels)))

	for i in range(args.iterations):
		next_batch = generate_test.next()
		test_tensors[i*args.batch_size:(i+1)*args.batch_size,:,:,:] = next_batch[0][args.tensor_map]
		test_labels[i*args.batch_size:(i+1)*args.batch_size,:] = next_batch[1]

	predictions = model.predict(test_tensors)
	print('prediction shape:', predictions.shape)

	melt_shape = (predictions.shape[0]*predictions.shape[1], predictions.shape[2])
	predictions = predictions.reshape(melt_shape)
	test_truth = test_labels.reshape(melt_shape)
	print('prediction shape:', predictions.shape)
	print('np sum truth:', np.sum(test_truth, axis=0), '\nnp sum pred :', np.sum(predictions, axis=0))
	
	pred_subset = []
	truth_subset = []
	for i in range(predictions.shape[0]):
		if test_truth[i][0] == 1 and np.argmax(predictions[i]) == 0:
			continue
		pred_subset.append(predictions[i])
		truth_subset.append(test_truth[i])

	print('np sum truth:', np.sum(np.array(truth_subset), axis=0), '\nnp sum pred :', np.sum(np.array(pred_subset), axis=0))
	
	plots.plot_roc_per_class_predictions(np.array(pred_subset), np.array(truth_subset), args.labels, args.id+'_no_reference_tp')
	plots.plot_roc_per_class_predictions(predictions, test_truth, args.labels, args.id)
	plots.plot_precision_recall_per_class_predictions(predictions, test_truth, args.labels, args.id)


def bqsr_train_tensor(args):
	'''Trains the bqsr tensor architecture on tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	This architecture looks at reads, flags and annotations.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping performance curves are plotted on the test dataset.
	'''
	args.labels = defines.base_labels_binary
	args.input_symbols = defines.bqsr_tensor_channel_map()

	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.bqsr_tensor_generator(args, train_paths)
	generate_valid = td.bqsr_tensor_generator(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_bqsr_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)
		
	test = td.load_bqsr_tensors_from_class_dirs(args, test_paths, per_class_max=1800)
	plots.plot_roc_per_class(model, test[0], test[1], args.labels, args.id)


def bqsr_train_annotation_tensor(args):
	'''Trains the bqsr tensor architecture on read tensors and annotations at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	This architecture looks at reads, flags and annotations.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping performance curves are plotted on the test dataset.
	'''
	args.labels = defines.base_labels_binary
	args.input_symbols = defines.bqsr_tensor_channel_map()
	args.annotations = defines.bqsr_annotations

	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.bqsr_tensor_annotation_generator(args, train_paths)
	generate_valid = td.bqsr_tensor_annotation_generator(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_bqsr_annotation_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)
		
	test = td.load_bqsr_tensors_annotations_from_class_dirs(args, test_paths, per_class_max=1800)
	plots.plot_roc_per_class(model, [test[0], test[1]], test[2], args.labels, args.id)


def bqsr_lstm_train_tensor(args):
	'''Trains the bqsr tensor architecture on tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	This architecture looks at reads, flags and annotations.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping performance curves are plotted on the test dataset.
	'''
	args.labels = defines.base_labels_binary
	args.input_symbols = defines.bqsr_tensor_channel_map()

	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.bqsr_tensor_generator(args, train_paths)
	generate_valid = td.bqsr_tensor_generator(args, valid_paths)

	model = models.build_bqsr_lstm_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)
		
	test = td.load_bqsr_tensors_from_class_dirs(args, test_paths, per_class_max=1800)
	plots.plot_roc_per_class(model, test[0], test[1], args.labels, args.id)


def train_ref_read_model(args):
	'''Trains a reference and read based architecture on tensors at the supplied data directory.

	This architecture looks at reads, and read flags.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping a performance curves are plotted on the test dataset.
	
	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	'''
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	in_channels = defines.total_input_channels_from_args(args)
	if args.channels_last:
		tensor_shape = (args.read_limit, args.window_size, in_channels)
	else:
		tensor_shape = (in_channels, args.read_limit, args.window_size) 

	generate_train = td.tensor_generator(args, train_paths, tensor_shape)
	generate_valid = td.tensor_generator(args, valid_paths, tensor_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_model(args)
	models.serialize_model_semantics(args, weight_path)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=800)
	plots.plot_roc_per_class(model, [test[0]], test[1], args.labels, args.id)


def train_ref_read_model_b(args):
	'''Trains a reference and read based architecture on tensors at the supplied data directory.

	This architecture looks at reads, and read flags.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping a performance curves are plotted on the test dataset.
	
	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	'''
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	in_channels = defines.total_input_channels_from_args(args)
	if args.channels_last:
		tensor_shape = (args.read_limit, args.window_size, in_channels)
	else:
		tensor_shape = (in_channels, args.read_limit, args.window_size) 

	generate_train = td.tensor_generator(args, train_paths, tensor_shape)
	generate_valid = td.tensor_generator(args, valid_paths, tensor_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.read_tensor_2d_model_from_args(args, 
									conv_width = 15, 
									conv_height = 15,
									conv_layers = [256, 128, 64],
									conv_dropout = 0.15,
									spatial_dropout = True,
									max_pools = [(1,3), (3,1)],
									padding='same',
									fc_layers = [12],
									fc_dropout = 0.01,
									batch_normalization = True)
	
	models.serialize_model_semantics(args, weight_path)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=800)
	plots.plot_roc_per_class(model, [test[0]], test[1], args.labels, args.id)



def train_ref_read_resnet_model(args):
	'''Trains a reference and read based architecture on tensors at the supplied data directory.

	This architecture looks at reads, and read flags.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping a performance curves are plotted on the test dataset.
	
	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	'''
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	in_channels = defines.total_input_channels_from_args(args)
	if args.channels_last:
		tensor_shape = (args.read_limit, args.window_size, in_channels)
	else:
		tensor_shape = (in_channels, args.read_limit, args.window_size) 

	generate_train = td.tensor_generator(args, train_paths, tensor_shape)
	generate_valid = td.tensor_generator(args, valid_paths, tensor_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_residual_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=800)
	plots.plot_roc_per_class(model, test[0], test[1], args.labels, args.id, batch_size=args.batch_size)


def train_ref_read_inception_model(args):
	'''Trains a reference and read based inception architecture on tensors at the supplied data directory.

	This architecture looks at reads, and read flags.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping a performance curves are plotted on the test dataset.
	
	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	'''
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	in_channels = defines.total_input_channels_from_args(args)
	if args.channels_last:
		tensor_shape = (args.read_limit, args.window_size, in_channels)
	else:
		tensor_shape = (in_channels, args.read_limit, args.window_size) 

	generate_train = td.tensor_generator(args, train_paths, tensor_shape)
	generate_valid = td.tensor_generator(args, valid_paths, tensor_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_inception_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=800)
	plots.plot_roc_per_class(model, test[0], test[1], args.labels, args.id, batch_size=args.batch_size)


def train_ref_read_dilated_model(args):
	'''Trains a reference and read based architecture on tensors at the supplied data directory.

	This architecture looks at reads, and read flags.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping a performance curves are plotted on the test dataset.
	
	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	'''
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	in_channels = defines.total_input_channels_from_args(args)
	if args.channels_last:
		tensor_shape = (args.read_limit, args.window_size, in_channels)
	else:
		tensor_shape = (in_channels, args.read_limit, args.window_size) 

	generate_train = td.tensor_generator(args, train_paths, tensor_shape)
	generate_valid = td.tensor_generator(args, valid_paths, tensor_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_dilated_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=800)
	plots.plot_roc_per_class(model, test[0], test[1], args.labels, args.id, batch_size=args.batch_size)


def train_ref_read_annotation_model(args):
	'''Trains a reference, read, and annotation CNN architecture on tensors at the supplied data directory.

	This architecture looks at reads, read flags, reference sequence, and variant annotations.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping performance curves are plotted on the test dataset.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	'''
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.tensor_generator_from_label_dirs_and_args(args, train_paths)
	generate_valid = td.tensor_generator_from_label_dirs_and_args(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)

	model = models.build_read_tensor_2d_and_annotations_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
	plots.plot_roc_per_class(model, [test[0], test[1]], test[2], args.labels, args.id, batch_size=args.batch_size)


def train_ref_read_annotation_exome_model(args):
	'''Trains a reference, read, and annotation CNN architecture on tensors at the supplied data directory.

	This architecture looks at reads, read flags, reference sequence, and variant annotations.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	After training with early stopping performance curves are plotted on the test dataset.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 

	'''	
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	in_channels = defines.total_input_channels_from_args(args)
	if args.channels_last:
		tensor_shape = (args.read_limit, args.window_size, in_channels)
	else:
		tensor_shape = (in_channels, args.read_limit, args.window_size) 

	generate_train = td.tensor_annotation_generator(args, train_paths, tensor_shape)
	generate_valid = td.tensor_annotation_generator(args, valid_paths, tensor_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_annotations_exome_model(args)

	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
	plots.plot_roc_per_class(model, [test[0], test[1]], test[2], args.labels, args.id, batch_size=args.batch_size)


def test_tensor_and_annotations_vs_filters(args):
	"""Evaluate the pure tensor architecture vs. Hard filters on a VCF file.

	Arguments:
		args.data_dir tensors to evaluate model
		args.negative_vcf VCF file with annotations to compare against
		args.train_vcf VCF file with true calls
		args.bed_file High confidence intervals for calls in args.train_vcf

	This architecture looks at reads, flags and annotations.
	Tensors must be generated by calling td.write_tensors() before this function is used.
	Performance curves for the CNN and for the filters are plotted on the test dataset.
	"""	
	_, _, test_paths = td.get_train_valid_test_paths(args)

	if args.annotations == '_':
		test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[2]
		model = models.build_read_tensor_2d_model(args)
		plots.plot_roc_per_class(model, [test[0]], test[1], args.labels, args.id)		
		cnn_predictions = model.predict([test[0]], batch_size=args.batch_size)	
	else:
		test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[3]
		model = models.build_read_tensor_2d_and_annotations_model(args)
		cnn_predictions = model.predict([test[0], test[1]], batch_size=args.batch_size)	

	cnn_snp_dict, cnn_indel_dict = models.predictions_to_snp_indel_scores(args, cnn_predictions, positions)
	snp_gatk_scores, indel_gatk_scores = td.scores_from_gatk_hard_filters(args, positions, distance_score=True)
	snp_gatk, indel_gatk = td.scores_from_gatk_hard_filters(args, positions)
	snp_heng_li, indel_heng_li = td.scores_from_heng_li_filters(args, positions)

	shared_snp_keys = [k for k in snp_heng_li.keys() if k in snp_gatk.keys() and k in snp_gatk_scores.keys()]
	shared_indel_keys = [k for k in indel_heng_li.keys() if k in indel_gatk.keys() and k in indel_gatk_scores.keys()]

	snp_scores = {}
	snp_truth = [snp_heng_li[p][1] for p in shared_snp_keys]
	snp_scores['GATK Signed Distance'] = [snp_gatk_scores[p][0] for p in shared_snp_keys]
	snp_scores['GATK Hard Filters'] = [snp_gatk[p][0] for p in shared_snp_keys]	
	snp_scores['Heng Li Hard Filters'] = [snp_heng_li[p][0] for p in shared_snp_keys]
	snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in shared_snp_keys]
	
	indel_scores = {}
	indel_truth = [indel_heng_li[p][1] for p in shared_indel_keys]	
	indel_scores['GATK Signed Distance'] = [indel_gatk_scores[p][0] for p in shared_indel_keys]
	indel_scores['GATK Hard Filters'] = [indel_gatk[p][0] for p in shared_indel_keys]
	indel_scores['Heng Li Hard Filters'] = [indel_heng_li[p][0] for p in shared_indel_keys]
	indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in shared_indel_keys]

	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP ROC '+args.id)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP Precision vs Recall '+args.id)
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL ROC '+args.id)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL Precision vs Recall '+args.id)


def test_tensor_vs_vcf(args):
	'''Evaluate the pure tensor architecture vs. Scores from a VCF file (e.g. VQSLOD).

	Arguments:
		args.data_dir tensors to evaluate model
		args.negative_vcf VCF file with scores to compare against
		args.train_vcf VCF file with true calls
		args.bed_file High confidence intervals for calls in args.train_vcf

	This architecture looks at reads, flags and annotations.
	Tensors must be generated by calling 
	td.nist_samples_to_tensors_flags_and_annotations(args) 
	before this function is used.
	Performance curves for CNN and VQSLOD are plotted on the test dataset.
	'''		
	_, _, test_paths = td.get_train_valid_test_paths(args)

	if args.annotations == '_':
		test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[2]
		model = models.build_read_tensor_2d_model(args)
		plots.plot_roc_per_class(model, [test[0]], test[1], args.labels, args.id)		
		cnn_predictions = model.predict([test[0]], batch_size=args.batch_size)	
	else:
		test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[3]
		model = models.build_read_tensor_2d_and_annotations_model(args)
		cnn_predictions = model.predict([test[0], test[1]], batch_size=args.batch_size)	

	cnn_snp_dict, cnn_indel_dict = models.predictions_to_snp_indel_scores(args, cnn_predictions, positions)
	snp_vqsr, indel_vqsr = td.scores_from_positions(args, positions)

	snp_scores = {}
	snp_truth = [snp_vqsr[p][1] for p in snp_vqsr.keys()]
	snp_scores['VQSR Single Sample'] = [snp_vqsr[p][0] for p in snp_vqsr.keys()]
	snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in snp_vqsr.keys()]
	
	indel_scores = {}
	indel_truth = [indel_vqsr[p][1] for p in indel_vqsr.keys()]	
	indel_scores['VQSR Single Sample'] = [indel_vqsr[p][0] for p in indel_vqsr.keys()]
	indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in indel_vqsr.keys()]

	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP ROC '+args.id)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP Precision vs Recall '+args.id)
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL ROC '+args.id)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL Precision vs Recall '+args.id)


def test_tensor_vs_multiple_vcfs(args):
	'''Evaluate the pure tensor architecture vs. Scores from a VCF file (e.g. VQSLOD).

	Arguments:
		args.data_dir tensors to evaluate model
		args.negative_vcf VCF file with scores to compare against
		args.train_vcf VCF file with true calls
		args.bed_file High confidence intervals for calls in args.train_vcf

	This architecture looks at reads, flags and annotations.
	Tensors must be generated by calling 
	td.nist_samples_to_tensors_flags_and_annotations(args) 
	before this function is used.
	Performance curves for CNN and VQSLOD are plotted on the test dataset.
	'''		
	_, _, test_paths = td.get_train_valid_test_paths(args)

	if args.annotations == '_':
		test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[2]
		model = models.build_read_tensor_2d_model(args)
		plots.plot_roc_per_class(model, [test[0]], test[1], args.labels, args.id)		
		cnn_predictions = model.predict([test[0]], batch_size=args.batch_size)	
	else:
		test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[3]
		model = models.build_read_tensor_2d_and_annotations_model(args)
		cnn_predictions = model.predict([test[0], test[1]], batch_size=args.batch_size)	

	cnn_snp_dict, cnn_indel_dict = models.predictions_to_snp_indel_scores(args, cnn_predictions, positions)
	
	snp_vqsr, indel_vqsr = td.scores_from_positions(args, positions)
	
	# if these don't exist, just call them the same so that they are still shared
	snp_vqsr_2, indel_vqsr_2 = snp_vqsr, indel_vqsr
	snp_vqsr_3, indel_vqsr_3 = snp_vqsr, indel_vqsr

	if args.negative_vcf_2: 
		snp_vqsr_2, indel_vqsr_2 = td.scores_from_positions(args, positions, override_vcf=args.negative_vcf_2)
	if args.negative_vcf_3: 
		snp_vqsr_3, indel_vqsr_3 = td.scores_from_positions(args, positions, override_vcf=args.negative_vcf_3)

	# get the positions that are in all of them.
	shared_snp_vqsr_keys = [k for k in snp_vqsr.keys() if k in snp_vqsr_2.keys() and k in snp_vqsr_3.keys()]
	shared_indel_vqsr_keys = [k for k in indel_vqsr.keys() if k in indel_vqsr_2.keys() and k in indel_vqsr_3.keys()]


	snp_scores = {}
	snp_truth = [snp_vqsr[p][1] for p in shared_snp_vqsr_keys]
	snp_scores['VQSR '+td.plain_name(args.negative_vcf)] = [snp_vqsr[p][0] for p in shared_snp_vqsr_keys]
	snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in shared_snp_vqsr_keys]

	indel_scores = {}
	indel_truth = [indel_vqsr[p][1] for p in shared_indel_vqsr_keys]	
	indel_scores['VQSR '+td.plain_name(args.negative_vcf)] = [indel_vqsr[p][0] for p in shared_indel_vqsr_keys]
	indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in shared_indel_vqsr_keys]
	
	if args.negative_vcf_2: 
		snp_scores['VQSR '+td.plain_name(args.negative_vcf_2)] = [snp_vqsr_2[p][0] for p in shared_snp_vqsr_keys]
		indel_scores['VQSR '+td.plain_name(args.negative_vcf_2)] = [indel_vqsr_2[p][0] for p in shared_indel_vqsr_keys]

	if args.negative_vcf_3:	
		snp_scores['VQSR '+td.plain_name(args.negative_vcf_2)] = [snp_vqsr_3[p][0] for p in shared_snp_vqsr_keys]
		indel_scores['VQSR '+td.plain_name(args.negative_vcf_2)] = [indel_vqsr_3[p][0] for p in shared_indel_vqsr_keys]

	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP ROC '+args.id)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP Precision vs Recall '+args.id)
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL ROC '+args.id)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL Precision vs Recall '+args.id)


def test_tensor_vs_gnomad(args):
	'''Evaluate the pure tensor architecture vs. gnomAD trained models (VQSR and Random Forest) and Deep Variant.

	This function compares against VQSR and random forest models trained with the gnomAD callset.
	Tensors must be generated by calling 
	td.nist_samples_to_tensors_flags_and_annotations(args) 
	before this function is used.
	Performance curves for CNN, VQSLOD, and AS_RF are plotted on the test dataset.

	Arguments
		args.data_dir: tensors to evaluate model
		args.negative_vcf: VCF file with scores to compare against
		args.train_vcf: VCF file with true calls
		args.bed_file: High confidence intervals for calls in args.train_vcf
		args.labels: The classification labels
		args.single_sample_vqsr: if True include VQSLOD from the negative VCF in comparison
		args.deep_variant_vcf: if set load this VCF and add it's QUAL scores to the comparison
	'''
	_, _, test_paths = td.get_train_valid_test_paths(args)

	if args.annotation_set == '_':
		test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[2]
		model = models.build_read_tensor_2d_model(args)
		cnn_predictions = model.predict([test[0]], batch_size=args.batch_size)	
	
	elif 'pileup' in args.id: # Ugly hack this should all be handled via the args.tensor_map
		test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples, dataset_id='pileup_tensor')
		positions = test[2]
		model = models.build_pileup_filter(args)
		cnn_predictions = model.predict(test[0], batch_size=args.batch_size)		
	
	else:
		test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[3]
		model = models.build_read_tensor_2d_and_annotations_model(args)
		cnn_predictions = model.predict([test[0], test[1]], batch_size=args.batch_size)


	snp_vqsr, indel_vqsr = td.gnomad_scores_from_positions(args, positions)
	snp_rf, indel_rf = td.gnomad_scores_from_positions(args, positions, score_key='AS_RF')

	snp_key_sets = [ set(snp_vqsr.keys()), set(snp_rf.keys()) ]
	indel_key_sets = [ set(indel_vqsr.keys()), set(indel_rf.keys()) ]

	if args.single_sample_vqsr:
		snp_single_sample, indel_single_sample = td.scores_from_positions(args, positions)
		snp_key_sets.append(set(snp_single_sample.keys()))
		indel_key_sets.append(set(indel_single_sample.keys()))

	if args.deep_variant_vcf:
		snp_deep_variant, indel_deep_variant = td.scores_from_positions(args, positions, 'QUAL', args.deep_variant_vcf)
		snp_key_sets.append(set(snp_deep_variant.keys()))
		indel_key_sets.append(set(indel_deep_variant.keys()))		

	shared_snp_keys = set.intersection(*snp_key_sets)
	shared_indel_keys = set.intersection(*indel_key_sets)

	snp_truth = [snp_vqsr[p][1] for p in shared_snp_keys]
	indel_truth = [indel_vqsr[p][1] for p in shared_indel_keys]

	if 'SNP' in args.labels:
		cnn_snp_dict = models.predictions_to_snp_scores(args, cnn_predictions, positions)
		snp_scores = {}
		snp_scores['VQSR gnomAD'] = [snp_vqsr[p][0] for p in shared_snp_keys]
		snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in shared_snp_keys]
		snp_scores['Random Forest'] = [snp_rf[p][0] for p in shared_snp_keys]
		if args.single_sample_vqsr:
			snp_scores['VQSR Single Sample'] = [snp_single_sample[p][0] for p in shared_snp_keys]
		if args.deep_variant_vcf:
			snp_scores['Deep Variant'] = [snp_deep_variant[p][0] for p in shared_snp_keys]

		if args.emit_interesting_sites:
			# Find CNN wrong RF and VQSR correct sites
			vqsr_thresh = (np.max(snp_scores['VQSR gnomAD']) + np.min(snp_scores['VQSR gnomAD']))/2
			cnn_thresh = (np.max(snp_scores['Neural Net']) + np.min(snp_scores['Neural Net']))/2
			rf_thresh = (np.max(snp_scores['Random Forest']) + np.min(snp_scores['Random Forest']))/2
			
			for p in shared_snp_keys:
				truth = snp_vqsr[p][1]
				vqsr_label = int(vqsr_thresh < snp_vqsr[p][0])
				cnn_label = int(cnn_thresh < cnn_snp_dict[p])
				rf_label = int(rf_thresh < snp_rf[p][0])
				if truth == rf_label and truth == vqsr_label and truth != cnn_label:
					print('CNN different label:', cnn_label,' and everyone else agrees on label:', truth,' at SNP:', p, 'CNN Score:', cnn_snp_dict[p])

			sorted_snps = sorted(cnn_snp_dict.items(), key=operator.itemgetter(1))
			for i in range(5):	
				print('Got Bad SNP score:', sorted_snps[i])
			for i in range(len(sorted_snps)-1, len(sorted_snps)-5, -1):	
				print('Got Good SNP score:', sorted_snps[i])
			print('Total true SNPs:', np.sum(snp_truth), ' Total false SNPs:', (len(snp_truth)-np.sum(snp_truth)))

		title_suffix = args.id+'_true_'+str(np.sum(snp_truth))+'_false_'+str(len(snp_truth)-np.sum(snp_truth))
		plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP_ROC_'+title_suffix)
		plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP_Precision_Recall_'+title_suffix)		
	
	if 'INDEL' in args.labels:
		cnn_indel_dict = models.predictions_to_indel_scores(args, cnn_predictions, positions)
		indel_scores = {}
		indel_scores['VQSR gnomAD'] = [indel_vqsr[p][0] for p in shared_indel_keys]
		indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in shared_indel_keys]
		indel_scores['Random Forest'] = [indel_rf[p][0] for p in shared_indel_keys]
		if args.single_sample_vqsr:
			indel_scores['VQSR Single Sample'] = [indel_single_sample[p][0] for p in shared_indel_keys]
		if args.deep_variant_vcf:
			indel_scores['Deep Variant'] = [indel_deep_variant[p][0] for p in shared_indel_keys]

		if args.emit_interesting_sites:
			# Find CNN wrong RF and VQSR correct sites
			vqsr_thresh = (np.max(indel_scores['VQSR gnomAD']) + np.min(indel_scores['VQSR gnomAD']))/2
			cnn_thresh = (np.max(indel_scores['Neural Net']) + np.min(indel_scores['Neural Net']))/2
			rf_thresh = (np.max(indel_scores['Random Forest']) + np.min(indel_scores['Random Forest']))/2
			for p in shared_indel_keys:
				truth = int(indel_vqsr[p][1])
				vqsr_label = int(vqsr_thresh < indel_vqsr[p][0])
				cnn_label = int(cnn_thresh < cnn_indel_dict[p])
				rf_label = int(rf_thresh < indel_rf[p][0])
				if truth == rf_label and truth == vqsr_label and truth != cnn_label:
					print('CNN different label:', cnn_label,' and everyone else agrees on label:', truth,' at INDEL:', p, 'CNN Score:', cnn_indel_dict[p])	

			sorted_indels = sorted(cnn_indel_dict.items(), key=operator.itemgetter(1))
			for i in range(5):	
				print('Got Bad INDEL score:', sorted_indels[i])
			for i in range(len(sorted_indels)-1, len(sorted_indels)-5, -1):	
				print('Got Good INDEL score:', sorted_indels[i])
			print('Total true INDELs:', np.sum(indel_truth), ' Total false INDELs:', (len(indel_truth)-np.sum(indel_truth)))
		
		title_suffix = args.id+'_true_'+str(np.sum(indel_truth))+'_false_'+str(len(indel_truth)-np.sum(indel_truth))
		plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL_ROC_'+title_suffix)
		plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL_Precision_Recall_'+title_suffix)


def test_refconv_vs_gnomad(args):
	"""Evaluate the refconv architecture vs. gnomAD trained models (VQSR and Random Forest).

	Arguments:
		args.data_dir tensors to evaluate model
		args.negative_vcf VCF file with scores to compare against
		args.train_vcf VCF file with true calls
		args.bed_file High confidence intervals for calls in args.train_vcf

	This function compares against VQSR and random forest models trained with the gnomAD callset.
	Tensors must be generated by calling 
	td.nist_samples_to_tensors_flags_and_annotations(args) 
	before this function is used.
	Performance curves for CNN, VQSLOD, and AS_RF are plotted on the test dataset.
	"""		
	_, _, test_paths = td.get_train_valid_test_paths(args)

	if args.window_size == 0:
		test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples, dataset_id='annotations')		
		model = models.build_annotation_multilayer_perceptron(args)
		positions = test[2]
		cnn_predictions = model.predict([test[0]], batch_size=64, verbose=0)
	
	elif args.annotation_set == '_':
		model = models.build_reference_model(args)
		test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples, dataset_id='reference')
		positions = test[2]
		cnn_predictions = model.predict([test[0]], batch_size=64, verbose=0)

	else:
		#model = models.build_reference_plus_model(args)
		model = models.build_reference_annotation_skip_model(args)	
		test = td.load_dna_annotations_positions_from_class_dirs(args, test_paths, per_class_max=args.samples)
		positions = test[3]
		cnn_predictions = model.predict([test[0], test[1]], batch_size=64, verbose=0)

	cnn_snp_dict, cnn_indel_dict = models.predictions_to_snp_indel_scores(args, cnn_predictions, positions)

	snp_vqsr, indel_vqsr = td.gnomad_scores_from_positions(args, positions)
	snp_rf, indel_rf = td.gnomad_scores_from_positions(args, positions, score_key='AS_RF')
	
	snp_key_sets = [ set(snp_vqsr.keys()), set(snp_rf.keys()) ]
	indel_key_sets = [ set(indel_vqsr.keys()), set(indel_rf.keys()) ]

	if args.single_sample_vqsr:
		snp_single_sample, indel_single_sample = td.scores_from_positions(args, positions)
		snp_key_sets.append(set(snp_single_sample.keys()))
		indel_key_sets.append(set(indel_single_sample.keys()))

	if args.deep_variant_vcf:
		snp_deep_variant, indel_deep_variant = td.scores_from_positions(args, positions, 'QUAL', args.deep_variant_vcf)
		snp_key_sets.append(set(snp_deep_variant.keys()))
		indel_key_sets.append(set(indel_deep_variant.keys()))

	shared_snp_keys = set.intersection(*snp_key_sets)
	shared_indel_keys = set.intersection(*indel_key_sets)

	snp_truth = [snp_rf[p][1] for p in shared_snp_keys]
	indel_truth = [indel_rf[p][1] for p in shared_indel_keys]

	snp_scores = {}
	snp_suffix = args.id+'_true_'+str(np.sum(snp_truth))+'_false_'+str(len(snp_truth)-np.sum(snp_truth))
	snp_scores['VQSR gnomAD'] = [snp_vqsr[p][0] for p in shared_snp_keys]
	snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in shared_snp_keys]
	snp_scores['Random Forest'] = [snp_rf[p][0] for p in shared_snp_keys]
	if args.single_sample_vqsr:
		snp_scores['VQSR Single Sample'] = [snp_single_sample[p][0] for p in shared_snp_keys]
	if args.deep_variant_vcf:
		snp_scores['Deep Variant'] = [snp_deep_variant[p][0] for p in shared_snp_keys]

	indel_scores = {}
	indel_suffix = args.id+'_true_'+str(np.sum(indel_truth))+'_false_'+str(len(indel_truth)-np.sum(indel_truth))
	indel_scores['VQSR gnomAD'] = [indel_vqsr[p][0] for p in shared_indel_keys]
	indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in shared_indel_keys]
	indel_scores['Random Forest'] = [indel_rf[p][0] for p in shared_indel_keys]
	if args.single_sample_vqsr:
		indel_scores['VQSR Single Sample'] = [indel_single_sample[p][0] for p in shared_indel_keys]
	if args.deep_variant_vcf:
		indel_scores['Deep Variant'] = [indel_deep_variant[p][0] for p in shared_indel_keys]

	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP_ROC_' + snp_suffix)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP_Precision_Recall_' + snp_suffix)
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL_ROC_' + indel_suffix)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL_Precision_Recall_' + indel_suffix)


def plot_vcf_roc(args):
	'''Plot ROC curves from a vcf annotated with scores.'''
	snp_scores, snp_truth, indel_scores, indel_truth = td.scores_from_vcf(args, args.score_keys)

	snp_suffix = args.id+'_true_'+str(np.sum(snp_truth))+'_false_'+str(len(snp_truth)-np.sum(snp_truth))
	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP_ROC_'+snp_suffix)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP_Precision_Recall_' + snp_suffix)

	indel_suffix = args.id+'_true_'+str(np.sum(indel_truth))+'_false_'+str(len(indel_truth)-np.sum(indel_truth))
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL_ROC_'+indel_suffix)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL_Precision_Recall_' + indel_suffix)


def plot_vcf_roc_gnomad_scores(args):
	'''Plot ROC and Precision-Recall curves from gnomAD vcfs annotated with scores.'''
	if args.single_sample_vqsr:
		args.score_keys.append('VQSR Single Sample')

	snp_scores, snp_truth, indel_scores, indel_truth = td.scores_from_gnomad_vcf(args, args.score_keys)
	
	snp_suffix = args.id+'_true_'+str(np.sum(snp_truth))+'_false_'+str(len(snp_truth)-np.sum(snp_truth))
	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP_ROC_'+snp_suffix)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP_Precision_Recall_'+snp_suffix)
	
	indel_suffix = args.id+'_true_'+str(np.sum(indel_truth))+'_false_'+str(len(indel_truth)-np.sum(indel_truth))
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL_ROC_'+indel_suffix)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL_Precision_Recall_'+indel_suffix)


def plot_vcf_roc_gnomad_like_scores(args):
	'''Plot ROC and Precision-Recall curves from a gnomAD-like vcf annotated with scores.'''	
	score_keys = ['AS_RF', 'VQSLOD', 'CNN_SCORE']

	if args.single_sample_vqsr:
		score_keys.append('VQSR Single Sample')

	snp_scores, snp_truth, indel_scores, indel_truth = td.scores_from_gnomad_like_vcf(args, score_keys)
	
	snp_suffix = args.id+'_true_'+str(np.sum(snp_truth))+'_false_'+str(len(snp_truth)-np.sum(snp_truth))
	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP_ROC_'+snp_suffix)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP_Precision_Recall_'+snp_suffix)
	
	indel_suffix = args.id+'_true_'+str(np.sum(indel_truth))+'_false_'+str(len(indel_truth)-np.sum(indel_truth))
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL_ROC_'+indel_suffix)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL_Precision_Recall_'+indel_suffix)


def plot_multi_vcf_roc(args, score_key='VQSLOD'):
	'''Plot ROCs from several VCFs'''		
	snp_scores = {}
	indel_scores = {}

	snp_data, indel_data, snp_data_2, indel_data_2, snp_data_3, indel_data_3 = td.concordance_scores_from_vcf(args, score_key)

	snp_scores[score_key+" "+td.plain_name(args.negative_vcf)] = snp_data['scores']
	indel_scores[score_key+" "+td.plain_name(args.negative_vcf)] = indel_data['scores']
	
	snp_scores[score_key+" "+td.plain_name(args.negative_vcf_2)] = snp_data_2['scores']
	indel_scores[score_key+" "+td.plain_name(args.negative_vcf_2)] = indel_data_2['scores']
	
	snp_scores[score_key+" "+td.plain_name(args.negative_vcf_2)] = snp_data_3['scores']
	indel_scores[score_key+" "+td.plain_name(args.negative_vcf_2)] = indel_data_3['scores']

	plots.plot_rocs_from_scores(snp_data['truth'], snp_scores, 'SNP ROC '+args.id)
	plots.plot_rocs_from_scores(indel_data['truth'], indel_scores, 'INDEL ROC '+args.id)


def test_tensor_and_annotations(args):
	'''Evaluate the tensor and annotation architecture on a test dataset.

	Arguments:
		args.data_dir tensors to evaluate model

	Tensors must be generated by calling 
	td.nist_samples_to_tensors_flags_and_annotations(args) 
	before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''			
	_, _, test_paths = td.get_train_valid_test_paths(args)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_and_annotations_model(args)
		
	test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
	plots.plot_roc_per_class(model, [test[0], test[1]], test[2], args.labels, args.id)


def test_ref_read_annotation_exome_model(args):
	'''Evaluate the tensor and annotation for exomes architecture on a test dataset.

	Arguments:
		args.data_dir tensors to evaluate model

	Tensors must be generated by calling 
	td.nist_samples_to_tensors_flags_and_annotations(args) 
	before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''			
	_, _, test_paths = td.get_train_valid_test_paths(args)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_annotations_exome_model(args)
		
	test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
	plots.plot_roc_per_class(model, [test[0], test[1]], test[2], args.labels, args.id)


def roc_curve_through_learning(args):
	"""Plot ROC curves during optimization.

	Arguments:
		args.data_dir tensors to train and evaluate model
		args.samples number of ROC curves to plot during training.

	Tensors must be generated by calling 
	td.nist_samples_to_tensors_flags_and_annotations(args) 
	before this function is used.
	"""		
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	in_channels = defines.total_input_channels_from_args(args)
	if args.channels_last:
		tensor_shape = (args.read_limit, args.window_size, in_channels)
	else:
		tensor_shape = (in_channels, args.read_limit, args.window_size) 

	generate_train = td.tensor_annotation_generator(args, train_paths, tensor_shape)
	generate_valid = td.tensor_annotation_generator(args, valid_paths, tensor_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_and_annotations_model(args)

	test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
	for i in range(args.epochs):
		model.fit_generator(generate_train, 
			samples_per_epoch=args.batch_size*2, nb_epoch=1, verbose=1, 
			nb_val_samples=args.batch_size, validation_data=generate_valid,
			callbacks=models.get_callbacks(weight_path, patience=4))
		plots.plot_roc_per_class(model, [test[0], test[1], test[2]], test[3], args.labels, args.id+str(i), prefix='./figures/animations/')

def roc_curve_through_learning(args):
	"""Plot ROC curves during optimization.

	Arguments:
		args.data_dir tensors to train and evaluate model
		args.samples number of ROC curves to plot during training.

	Tensors must be generated by calling 
	td.nist_samples_to_tensors_flags_and_annotations(args) 
	before this function is used.
	"""		
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	in_channels = defines.total_input_channels_from_args(args)
	if args.channels_last:
		tensor_shape = (args.read_limit, args.window_size, in_channels)
	else:
		tensor_shape = (in_channels, args.read_limit, args.window_size) 

	generate_train = td.tensor_annotation_generator(args, train_paths, tensor_shape)
	generate_valid = td.tensor_annotation_generator(args, valid_paths, tensor_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_read_tensor_2d_and_annotations_model(args)

	test = td.load_tensors_and_annotations_from_class_dirs(args, test_paths, per_class_max=args.samples)
	for i in range(args.iterations):
		model.fit_generator(generate_train, 
			samples_per_epoch=args.batch_size*2, nb_epoch=1, verbose=1, 
			nb_val_samples=args.batch_size, validation_data=generate_valid,
			callbacks=models.get_callbacks(weight_path, patience=4))
		plots.plot_roc_per_class(model, [test[0], test[1], test[2]], test[3], args.labels, args.id+str(i), prefix='./figures/animations/')


def roc_curve_through_learning_segmentation(args):
	"""Plot ROC curves during optimization of segmenting architecture.

	Arguments:
		args.data_dir tensors to train and evaluate model
		args.samples number of ROC curves to plot during training.
	"""		
	args.labels = defines.calling_labels
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths_all(args)

	generate_train = td.calling_tensors_generator(args, train_paths)
	generate_valid = td.calling_tensors_generator(args, valid_paths)
	generate_test = td.calling_tensors_generator(args, test_paths)

	model = models.build_2d_cnn_calling_segmentation_1d(args)

	test_tensors = np.zeros((args.iterations*args.batch_size,) + defines.tensor_shape_from_args(args))
	test_labels = np.zeros((args.iterations*args.batch_size, args.window_size, len(args.labels)))

	for i in range(args.iterations):
		next_batch = generate_test.next()
		test_tensors[i*args.batch_size:(i+1)*args.batch_size,:,:,:] = next_batch[0][args.tensor_map]
		test_labels[i*args.batch_size:(i+1)*args.batch_size,:] = next_batch[1]

	melt_shape = (test_labels.shape[0]*test_labels.shape[1], test_labels.shape[2])

	for i in range(args.samples):
		predictions = model.predict(test_tensors)
		predictions = predictions.reshape(melt_shape)
		test_truth = test_labels.reshape(melt_shape)
		plots.plot_precision_recall_per_class_predictions(predictions, test_truth, args.labels, args.id+str(i), prefix='./figures/animations/')
		model.fit_generator(generate_train, 
			steps_per_epoch=args.batch_size, epochs=1, verbose=1, 
			validation_steps=args.batch_size*8, validation_data=generate_valid)


def depristo_inception(args):
	"""Trains the deep variant architecture on tensors at the supplied data directory.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		args.read_limit: Max number of reads to use (height of the png).
		args.window_size: sequence window around variant (width of the png).
	This architecture looks at pngs of read level data.
	(See: http://biorxiv.org/content/early/2016/12/14/092890).
	Tensors must be generated by calling: td.nist_samples_to_png(args)
	before this function is used.
	After training with early stopping a performance curves are plotted on the test dataset.
	"""	
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	image_shape = (args.read_limit, args.window_size)
	generate_train = td.image_generator(args, train_paths, shape=image_shape)
	generate_valid = td.image_generator(args, valid_paths, shape=image_shape)

	weight_path = arguments.weight_path_from_args(args)
	model = models.inception_v3_max(args, architecture=args.weights_hd5)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)
		
	test = td.load_images_from_class_dirs(args, test_paths, shape=image_shape, per_class_max=args.samples)
	plots.plot_roc_per_class(model, test[0], test[1], args.labels, args.id)


def make_annotation_multilayer_perceptron(args):
	'''Train a Multilayer Perceptron (MLP) Annotation architecture (no convolutions).

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		
	Annotation tensors must be generated by calling 
	td.write_dna_tensors(include_dna=False) before this function is used.
	Performance curves for MLP are plotted on the test dataset.
	'''		
	args.window_size = 0
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.dna_annotation_generator(args, train_paths)
	generate_valid = td.dna_annotation_generator(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)
	#model = models.build_annotation_multilayer_perceptron(args)
	model = models.annotation_multilayer_perceptron_from_args(args,
											fc_layers = [128],
											dropout = 0.3,
											skip_connection = True,
											batch_normalization = True)

	models.inspect_model(args, model, generate_train, generate_valid)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)
	
	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples, dataset_id='annotations')
	plots.plot_roc_per_class(model, test[0], test[1], args.labels, args.id)


def make_reference_net(args):
	'''Train a 1D Convolution architecture on reference tracks.

	Arguments
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		
	Tensors must be generated by calling 
	td.write_dna_multisource_annotations() 
	before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''	
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.dna_annotation_generator(args, train_paths)
	generate_valid = td.dna_annotation_generator(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_reference_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples, dataset_id='reference')
	plots.plot_roc_per_class(model, test[0], test[1], args.labels, args.id)


def make_reference_annotation_net(args):
	'''Train a 1D Convolution plus reference tracks and MLP Annotation architecture.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		
	Annotation tensors must be generated by calling 
	td.write_dna_multisource_annotations() before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''	
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.dna_annotation_generator(args, train_paths)
	generate_valid = td.dna_annotation_generator(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_reference_plus_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_dna_annotations_positions_from_class_dirs(args, test_paths, per_class_max=args.samples)
	plots.plot_roc_per_class(model, [test[0], test[1]], test[2], args.labels, args.id)


def train_reference_plus_skip(args):
	'''Train a 1D Convolution plus MLP Annotation with skip connection architecture.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		
	Annotation tensors must be generated by calling 
	td.write_dna_multisource_annotations() before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''	
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.dna_annotation_generator(args, train_paths)
	generate_valid = td.dna_annotation_generator(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_reference_annotation_skip_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_dna_annotations_positions_from_class_dirs(args, test_paths, per_class_max=args.samples)
	plots.plot_roc_per_class(model, [test[0], test[1]], test[2], args.labels, args.id)	


def make_reference_annotation_net_1layer(args):
	'''Train a 1D Convolution plus reference tracks and MLP Annotation architecture.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		
	Annotation tensors must be generated by calling 
	td.write_dna_multisource_annotations() before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''	
	train_paths, valid_paths, test_paths = td.get_train_valid_test_paths(args)

	generate_train = td.dna_annotation_generator(args, train_paths)
	generate_valid = td.dna_annotation_generator(args, valid_paths)

	weight_path = arguments.weight_path_from_args(args)
	model = models.build_reference_1d_1layer_model(args)
	model = models.train_model_from_generators(args, model, generate_train, generate_valid, weight_path)

	test = td.load_dna_annotations_positions_from_class_dirs(args, test_paths, per_class_max=args.samples)
	plots.plot_roc_per_class(model, test[0], test[2], args.labels, args.id)


def test_reference_annotation_net(args):
	'''Test the 1D Convolution and MLP Annotation architecture.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		
	Annotation tensors must be generated by calling 
	td.write_dna_tensors() before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''		
	weight_path = arguments.weight_path_from_args(args)
	model = models.build_reference_plus_model(args)
	
	test_dir = args.data_dir + 'test/'
	test_paths = [test_dir + vp for vp in sorted(os.listdir(test_dir)) if os.path.isdir(test_dir + vp)]

	title = plots.weight_path_to_title(weight_path)
	test = td.load_dna_annotations_positions_from_class_dirs(args, test_paths, per_class_max=args.samples)
	positions = test[3]

	cnn_predictions = model.predict([test[0], test[1]], batch_size=64, verbose=0)
	cnn_snp_dict, cnn_indel_dict = models.predictions_to_snp_indel_scores(args, cnn_predictions, positions)
	snp_heng_li, indel_heng_li = td.scores_from_positions(args, positions)

	snp_scores = {}
	snp_truth = [snp_heng_li[p][1] for p in snp_heng_li.keys()]
	snp_scores['VQSR'] = [snp_heng_li[p][0] for p in snp_heng_li.keys()]
	snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in snp_heng_li.keys()]
	
	indel_scores = {}
	indel_truth = [indel_heng_li[p][1] for p in indel_heng_li.keys()]	
	indel_scores['VQSR'] = [indel_heng_li[p][0] for p in indel_heng_li.keys()]
	indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in indel_heng_li.keys()]

	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP ROC '+args.id)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP Precision vs Recall '+args.id)
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL ROC '+args.id)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL Precision vs Recall '+args.id)


def test_reference_net(args):
	'''Test the 1D Convolution on reference sequence architecture.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		
	Tensors must be generated by calling 
	td.write_dna_tensors() before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''		
	weight_path = arguments.weight_path_from_args(args)
	model = models.build_reference_model(args)
	
	test_dir = args.data_dir + 'test/'
	test_paths = [test_dir + vp for vp in sorted(os.listdir(test_dir)) if os.path.isdir(test_dir + vp)]

	title = plots.weight_path_to_title(weight_path)
	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples, dataset_id='reference')
	positions = test[2]

	cnn_predictions = model.predict([test[0]], batch_size=args.batch_size)
	cnn_snp_dict, cnn_indel_dict = models.predictions_to_snp_indel_scores(args, cnn_predictions, positions)
	snp_heng_li, indel_heng_li = td.scores_from_positions(args, positions)

	snp_scores = {}
	snp_truth = [snp_heng_li[p][1] for p in snp_heng_li.keys()]
	snp_scores['VQSR'] = [snp_heng_li[p][0] for p in snp_heng_li.keys()]
	snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in snp_heng_li.keys()]
	
	indel_scores = {}
	indel_truth = [indel_heng_li[p][1] for p in indel_heng_li.keys()]	
	indel_scores['VQSR'] = [indel_heng_li[p][0] for p in indel_heng_li.keys()]
	indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in indel_heng_li.keys()]

	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP ROC '+args.id)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP Precision vs Recall '+args.id)
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL ROC '+args.id)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL Precision vs Recall '+args.id)


def test_annotation_multilayer_perceptron(args):
	'''Test the 1D Convolution on reference sequence architecture.

	Arguments:
		args.data_dir: must be set to an appropriate directory with
			subdirectories of test, valid and train, each containing
			subdirectories for each label with tensors stored as hd5 files. 
		
	Tensors must be generated by calling 
	td.write_dna_tensors() before this function is used.
	Performance curves for CNN are plotted on the test dataset.
	'''		
	weight_path = arguments.weight_path_from_args(args)
	model = models.build_annotation_multilayer_perceptron(args)
	
	test_dir = args.data_dir + 'test/'
	test_paths = [test_dir + vp for vp in sorted(os.listdir(test_dir)) if os.path.isdir(test_dir + vp)]

	title = plots.weight_path_to_title(weight_path)
	test = td.load_tensors_from_class_dirs(args, test_paths, per_class_max=args.samples, dataset_id='annotations')
	positions = test[2]

	cnn_predictions = model.predict([test[0]], batch_size=args.batch_size)
	cnn_snp_dict, cnn_indel_dict = models.predictions_to_snp_indel_scores(args, cnn_predictions, positions)
	snp_heng_li, indel_heng_li = td.scores_from_positions(args, positions)

	snp_scores = {}
	snp_truth = [snp_heng_li[p][1] for p in snp_heng_li.keys()]
	snp_scores['VQSR'] = [snp_heng_li[p][0] for p in snp_heng_li.keys()]
	snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in snp_heng_li.keys()]
	
	indel_scores = {}
	indel_truth = [indel_heng_li[p][1] for p in indel_heng_li.keys()]	
	indel_scores['VQSR'] = [indel_heng_li[p][0] for p in indel_heng_li.keys()]
	indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in indel_heng_li.keys()]

	plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP ROC '+args.id)
	plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP Precision vs Recall '+args.id)
	plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL ROC '+args.id)
	plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL Precision vs Recall '+args.id)


def inference_with_architectures(args):
	'''Perform inference as defined by the architecture configuration files

	Arguments:
			args.architectures: list of architecture semantics config files
	'''
	vcf_reader = pysam.VariantFile(args.negative_vcf, "r")
	vcf_writer = pysam.VariantFile(args.output_vcf, 'w', header=vcf_reader.header)

	for a in args.architectures:
		score_key = a.split('.')[-2]
		vcf_reader.header.info.add(score_key, "1", "Float", "Score from Neural Network "+score_key)
		_, _, test_generator = td.train_valid_test_generators_from_args(args, with_positions=True)
		model = models.set_args_and_get_model_from_semantics(args, a)


def test_architectures(args):
	'''Evaluate architectures defined by architecture configuration files

	Compares against VQSR, gnomAD VQSR and Random Forest, and deep variant.

	Arguments:
			args.architectures: list of architecture semantics config files
	'''
	for a in args.architectures:
		_, _, test_generator = td.train_valid_test_generators_from_args(args, with_positions=True)
		test = td.big_batch_from_minibatch_generator(args, test_generator, with_positions=True)
		model = models.set_args_and_get_model_from_semantics(args, a)
		positions = test[-1]
		test_data = [test[0][args.tensor_map], test[0]['annotations']]

		cnn_predictions = model.predict(test_data, batch_size=args.batch_size)
		cnn_snp_dict, cnn_indel_dict = models.predictions_to_snp_indel_scores(args, cnn_predictions, positions)

		snp_vqsr, indel_vqsr = td.gnomad_scores_from_positions(args, positions)
		snp_rf, indel_rf = td.gnomad_scores_from_positions(args, positions, score_key='AS_RF')

		snp_key_sets = [ set(snp_vqsr.keys()), set(snp_rf.keys()) ]
		indel_key_sets = [ set(indel_vqsr.keys()), set(indel_rf.keys()) ]

		if args.single_sample_vqsr:
			snp_single_sample, indel_single_sample = td.scores_from_positions(args, positions)
			snp_key_sets.append(set(snp_single_sample.keys()))
			indel_key_sets.append(set(indel_single_sample.keys()))

		if args.deep_variant_vcf:
			snp_deep_variant, indel_deep_variant = td.scores_from_positions(args, positions, 'QUAL', args.deep_variant_vcf)
			snp_key_sets.append(set(snp_deep_variant.keys()))
			indel_key_sets.append(set(indel_deep_variant.keys()))		

		shared_snp_keys = set.intersection(*snp_key_sets)
		shared_indel_keys = set.intersection(*indel_key_sets)

		snp_truth = [snp_deep_variant[p][1] for p in shared_snp_keys]
		indel_truth = [indel_deep_variant[p][1] for p in shared_indel_keys]
		
		if 'SNP' in args.labels:
			snp_scores = {}
			snp_scores['VQSR gnomAD'] = [snp_vqsr[p][0] for p in shared_snp_keys]
			snp_scores['Neural Net'] = [cnn_snp_dict[p] for p in shared_snp_keys]
			snp_scores['Random Forest'] = [snp_rf[p][0] for p in shared_snp_keys]
			if args.single_sample_vqsr:
				snp_scores['VQSR Single Sample'] = [snp_single_sample[p][0] for p in shared_snp_keys]
			if args.deep_variant_vcf:
				snp_scores['Deep Variant'] = [snp_deep_variant[p][0] for p in shared_snp_keys]

			if args.emit_interesting_sites:
				# Find CNN wrong RF and VQSR correct sites
				vqsr_thresh = (np.max(snp_scores['VQSR gnomAD']) + np.min(snp_scores['VQSR gnomAD']))/2
				cnn_thresh = (np.max(snp_scores['Neural Net']) + np.min(snp_scores['Neural Net']))/2
				rf_thresh = (np.max(snp_scores['Random Forest']) + np.min(snp_scores['Random Forest']))/2
				
				for p in shared_snp_keys:
					truth = snp_vqsr[p][1]
					vqsr_label = int(vqsr_thresh < snp_vqsr[p][0])
					cnn_label = int(cnn_thresh < cnn_snp_dict[p])
					rf_label = int(rf_thresh < snp_rf[p][0])
					if truth == rf_label and truth == vqsr_label and truth != cnn_label:
						print('CNN different label:', cnn_label,' and everyone else agrees on label:', truth,' at SNP:', p, 'CNN Score:', cnn_snp_dict[p])

				sorted_snps = sorted(cnn_snp_dict.items(), key=operator.itemgetter(1))
				for i in range(5):	
					print('Got Bad SNP score:', sorted_snps[i])
				for i in range(len(sorted_snps)-1, len(sorted_snps)-5, -1):	
					print('Got Good SNP score:', sorted_snps[i])
				print('Total true SNPs:', np.sum(snp_truth), ' Total false SNPs:', (len(snp_truth)-np.sum(snp_truth)))

			title_suffix = a.split('/')[-1].split('.')[0] +'_'+ args.id+'_true_'+str(np.sum(snp_truth))+'_false_'+str(len(snp_truth)-np.sum(snp_truth))
			plots.plot_rocs_from_scores(snp_truth, snp_scores, 'SNP_ROC_'+title_suffix)
			plots.plot_precision_recall_from_scores(snp_truth, snp_scores, 'SNP_Precision_Recall_'+title_suffix)		
		
		if 'INDEL' in args.labels:
			indel_scores = {}
			indel_scores['VQSR gnomAD'] = [indel_vqsr[p][0] for p in shared_indel_keys]
			indel_scores['Neural Net'] = [cnn_indel_dict[p] for p in shared_indel_keys]
			indel_scores['Random Forest'] = [indel_rf[p][0] for p in shared_indel_keys]
			if args.single_sample_vqsr:
				indel_scores['VQSR Single Sample'] = [indel_single_sample[p][0] for p in shared_indel_keys]
			if args.deep_variant_vcf:
				indel_scores['Deep Variant'] = [indel_deep_variant[p][0] for p in shared_indel_keys]

			if args.emit_interesting_sites:
				# Find CNN wrong RF and VQSR correct sites
				vqsr_thresh = (np.max(indel_scores['VQSR gnomAD']) + np.min(indel_scores['VQSR gnomAD']))/2
				cnn_thresh = (np.max(indel_scores['Neural Net']) + np.min(indel_scores['Neural Net']))/2
				rf_thresh = (np.max(indel_scores['Random Forest']) + np.min(indel_scores['Random Forest']))/2
				for p in shared_indel_keys:
					truth = int(indel_vqsr[p][1])
					vqsr_label = int(vqsr_thresh < indel_vqsr[p][0])
					cnn_label = int(cnn_thresh < cnn_indel_dict[p])
					rf_label = int(rf_thresh < indel_rf[p][0])
					if truth == rf_label and truth == vqsr_label and truth != cnn_label:
						print('CNN different label:', cnn_label,' and everyone else agrees on label:', truth,' at INDEL:', p, 'CNN Score:', cnn_indel_dict[p])	

				sorted_indels = sorted(cnn_indel_dict.items(), key=operator.itemgetter(1))
				for i in range(5):	
					print('Got Bad INDEL score:', sorted_indels[i])
				for i in range(len(sorted_indels)-1, len(sorted_indels)-5, -1):	
					print('Got Good INDEL score:', sorted_indels[i])
				print('Total true INDELs:', np.sum(indel_truth), ' Total false INDELs:', (len(indel_truth)-np.sum(indel_truth)))
			
			title_suffix = a.split('/')[-1].split('.')[0] +'_'+ args.id+'_true_'+str(np.sum(indel_truth))+'_false_'+str(len(indel_truth)-np.sum(indel_truth))
			plots.plot_rocs_from_scores(indel_truth, indel_scores, 'INDEL_ROC_'+title_suffix)
			plots.plot_precision_recall_from_scores(indel_truth, indel_scores, 'INDEL_Precision_Recall_'+title_suffix)


# Back to the top!
if "__main__" == __name__:
	run()