"""Script for encoding a payload into an image."""

import argparse
import pathlib

from PIL import Image, ImageMath

import utilities


def argument_parser() -> argparse.ArgumentParser:
    """Returns a configured argparser.ArgumentParser for this program."""
    parser = argparse.ArgumentParser(
        description='Encode SECRETS into a picture',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'host_image',
        type=pathlib.Path,
        help='The image that will hide the information.')
    parser.add_argument(
        'payload_image',
        type=pathlib.Path,
        help='The image that will be hidden within the host image.')
    parser.add_argument(
        '--significant_digits',
        type=int,
        default=1,
        help='The number of least significant digits available to encode over.')
    parser.add_argument(
        '--display',
        action='store_true',
        default=False,
        help='Display the encoded image generated by this program.')
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save the encoded image generated by this program.')
    parser.add_argument(
        '--output_dir',
        type=pathlib.Path,
        default='.',
        help=(
            'A specific location to which the processed image will be saved. '
            'If not specified, the current working directory will be used.'))

    return parser


def encode(host: Image, payload: Image, n_significant_digits: int) -> Image:
    """Encode a payload into an image (using the last n_significant_digits)."""
    output_rgb_channels = []
    for host_channel, payload_channel in zip(host.split(), payload.split()):
        # Mask out all but the least significant byte, encoding payload there
        mask = utilities.bit_mask(n_significant_digits)
        expression = (
            "convert("
                "(host & ({rgb_range} - {mask})) "
                "| (payload & {mask}), 'L')".format(
                    rgb_range=utilities.RGB_RANGE, mask=mask))
        output_rgb_channels.append(
            ImageMath.eval(
                expression,
                host=host_channel,
                payload=payload_channel))
    return Image.merge('RGB', output_rgb_channels)


def main():
    args = argument_parser().parse_args()

    host = Image.open(args.host_image)
    payload = Image.open(args.payload_image)

    encoded = encode(host, payload, args.significant_digits)

    # Display the encoded image
    if args.display:
        encoded.show()

    # Save the encoded image, if the user wants us to
    if args.save:
        user_response = utilities.query_user(
            'GONNA SAVE ENCODED IMAGE to "{0:s}"; GAR, IS THAT K???'.format(
                str(args.output_dir.absolute()))))
        if user_response:
            p = args.host_image  # Short reference to the host_image path
            filename = '{0:s}{1:s}{2:s}'.format(p.stem, '.encoded', p.suffix)
            encoded.save(
                args.output_dir.joinpath(filename), format='png', quality=100)


if __name__ == '__main__':
    main()
