import { ScanLabelView } from '../../../components/ScanLabelView';

export default function ScanLabelPage({ params }: { params: { labelCode: string } }) {
  return <ScanLabelView labelCode={params.labelCode} />;
}
