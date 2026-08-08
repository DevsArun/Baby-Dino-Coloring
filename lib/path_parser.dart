import 'dart:ui';

/// Parses the strict subset of SVG path data used by our page generator:
/// absolute M, L, C, Q and Z commands only.
Path parseSvgPath(String d) {
  final path = Path();
  final tokens = _tokenize(d);
  var i = 0;
  var cx = 0.0;
  var cy = 0.0;

  double num_() {
    final t = tokens[i];
    i++;
    return double.parse(t);
  }

  while (i < tokens.length) {
    final t = tokens[i];
    switch (t) {
      case 'M':
        i++;
        cx = num_();
        cy = num_();
        path.moveTo(cx, cy);
        break;
      case 'L':
        i++;
        cx = num_();
        cy = num_();
        path.lineTo(cx, cy);
        break;
      case 'C':
        i++;
        final x1 = num_();
        final y1 = num_();
        final x2 = num_();
        final y2 = num_();
        cx = num_();
        cy = num_();
        path.cubicTo(x1, y1, x2, y2, cx, cy);
        break;
      case 'Q':
        i++;
        final x1 = num_();
        final y1 = num_();
        cx = num_();
        cy = num_();
        path.quadraticBezierTo(x1, y1, cx, cy);
        break;
      case 'Z':
        i++;
        path.close();
        break;
      default:
        // Unknown token: skip defensively.
        i++;
        break;
    }
  }
  return path;
}

List<String> _tokenize(String d) {
  final tokens = <String>[];
  final buf = StringBuffer();

  void flush() {
    if (buf.isNotEmpty) {
      tokens.add(buf.toString());
      buf.clear();
    }
  }

  for (var k = 0; k < d.length; k++) {
    final ch = d[k];
    if (ch == 'M' || ch == 'L' || ch == 'C' || ch == 'Q' || ch == 'Z') {
      flush();
      tokens.add(ch);
    } else if (ch == ' ' || ch == ',' || ch == '\n') {
      flush();
    } else {
      buf.write(ch);
    }
  }
  flush();
  return tokens;
}
