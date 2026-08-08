import 'package:baby_dino_coloring/path_parser.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('parses M L Z into a closed triangle path', () {
    final path = parseSvgPath('M 0 0 L 100 0 L 50 100 Z');
    expect(path.contains(const Offset(50, 30)), isTrue);
    expect(path.contains(const Offset(5, 95)), isFalse);
  });

  test('parses cubic ellipse and hit-tests center', () {
    const d = 'M 200 100 '
        'C 200 155.2 155.2 200 100 200 '
        'C 44.8 200 0 155.2 0 100 '
        'C 0 44.8 44.8 0 100 0 '
        'C 155.2 0 200 44.8 200 100 Z';
    final path = parseSvgPath(d);
    expect(path.contains(const Offset(100, 100)), isTrue);
    expect(path.contains(const Offset(3, 3)), isFalse);
  });

  test('parses quadratic curves', () {
    final path = parseSvgPath('M 0 100 Q 50 0 100 100 Z');
    expect(path.contains(const Offset(50, 80)), isTrue);
  });
}
