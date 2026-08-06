import React from 'react';

interface ImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  fill?: boolean;
  style?: React.CSSProperties;
  priority?: boolean;
  quality?: number | string;
  placeholder?: string;
  blurDataURL?: string;
  loader?: (props: { src: string; width: number; quality?: number }) => string;
  sizes?: string;
  unoptimized?: boolean;
}

export default function Image({ src, alt, width, height, fill, style, priority, quality, placeholder, blurDataURL, loader, sizes, unoptimized, ...rest }: ImageProps) {
  const finalSrc = loader ? loader({ src: Number(width) || 0, quality: quality ? Number(quality) : undefined }) : src;

  if (fill) {
    return (
      <img
        src={finalSrc}
        alt={alt}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          ...style,
        }}
        {...rest}
      />
    );
  }

  return (
    <img
      src={finalSrc}
      alt={alt}
      width={width}
      height={height}
      style={style}
      {...rest}
    />
  );
}
