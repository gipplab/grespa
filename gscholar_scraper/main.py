import scrapy.cmdline as cmdline
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start spider process(es).')
    parser.add_argument('--settings','-s', type=str, help='additional settings arguments')
    parser.add_argument('--spider_parameters', '-a', type=str, help='additional spider arguments')
    parser.add_argument('--output_filename','-o', type=str, help='filename for export')
    parser.add_argument('--output_filetype','-t', type=str, help='file type for export')
    parser.add_argument('--log_level', '-L', type=str, help='log level')

    parser.add_argument('spider', metavar='-c', type=str, help='name of the spider to run')
    # cmdline.execute('scrapy crawl authorLabels -s JOBDIR=crawls/author_labels -o popular_names.csv -t csv'.split(' '))
    args = parser.parse_args()

    command = 'scrapy crawl %s' % args.spider
    if args.spider_parameters:
        command += ' -a %s' % args.spider_parameters
    if args.settings:
        command += ' -s %s' % args.settings
    if args.output_filename:
        command += ' -t %s' % args.output_filename
    if args.output_filetype:
        command += ' -o %s' % args.output_filetype
    if args.log_level:
        command += ' -L %s' % args.log_level
    print 'executing: %s ' % command
    cmdline.execute(command.split(' '))
