import { combineLatest, merge, Observable, of, ReplaySubject, Subject, throwError } from 'rxjs';

import {
  delay,
  filter,
  map,
  mergeMap,
  retryWhen,
  startWith,
  switchMap,
  take,
  takeUntil,
  tap,
  withLatestFrom,
} from 'rxjs/operators';
import { ChangeDetectionStrategy, Component, OnDestroy, TemplateRef, ViewChild, ViewContainerRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { select, Store } from '@ngrx/store';

import { OverlayGlobalService } from '@core/services/overlay-global.service';
import { Dict, diffObject, hasId, isEmpty, pluckId } from '@shared/utils/common.utils';
import { Anchor } from '@shared/models/anchor.model';
import { Id } from '@shared/models/id.model';
import {
  MeterNormalized,

} from '@shared/models/meters';
import { DataSelectors } from '@data/selectors';
import * as fromMeterManagement from '../../reducers';
import { GraphLayoutService, GraphPort } from '../../../graph/services/graph-layout.service';
import { inputToOutput, not, sameNode } from '../../../graph/rules';
import { PortConnectionRule } from '../../../graph/model/rule.model';
import { alwaysFalse } from '../../../graph/rules/common.rules';
import { MeterConfigMeta } from '../../models/data.model';
import { TextResolver } from '../../../graph/components/port-graph/port-graph.component';
import { DialogContext, FormProcessor, MeterConfigComponent } from '../meter-config/meter-config.component';

import {
  fieldsToRemoveOnSave,
  getConstantFieldKey,
  getFormFields,
  getUseConstantFieldKey,
} from '../../utils/meter-config.utils';
import { serializeChanges, squashChanges } from '../../utils/changesets.utils';
import { MeterMgmtActions } from '../../actions';
import {
  ConfigEditorNodeDialogSelectors,
  ConfigEditorSelectors,
  DataSelectors as MeterMgmtDataSelectors,
  MetersListSelectors,
} from '../../selectors';

import { FormControl, FormGroup, Validators } from '@angular/forms';
import { AutonameService } from '../../services/autoname.service';
import { ChangesComponent } from '@core/guards/prevent-unsaved-changes.guard';
import { Connection } from '../../../graph/model/connection.model';
import { createLimitsValidator, LimitsValidatorService } from '../../services/limits-validator.service';
import { OverlayConnectedService } from '@core/services/overlay-connected.service';
import { CdkOverlayOrigin, ComponentType } from '@angular/cdk/overlay';
import * as fromLayout from '../../../layout/reducers/layout.reducer';
import { OverlayPointService, PointOverlayContext } from '@core/services/overlay-point.service';
import { dropdownPanel } from '@components/dropdown-search/dropdown-search.animations';
import { createDatesValidator, DatesValidatorService } from '../../services/dates-validator.service';
import { createParserValidator, ParserValidatorService } from '../../services/parser-validator.service';
import {
  createTableNameValidator,
  TableNameValidatorService,
} from '../../services/database-table-validator.service';
import { TestResultComponent, TestResultContext } from '../../components/test-result/test-result.component';
import { MeterModelParserHelpComponent } from '../../components/meter-model-parser-help/meter-model-parser-help.component';
import { ClosableDialog } from '@core/components/overlay.component';
import { InputPortNormalized, MeterConfig, MeterConfigType, OutputPortNormalized } from '../../models/meter-config.model';

type MeterConfigPort = GraphPort<InputPortNormalized | OutputPortNormalized, MeterConfig>;

/* eslint-disable max-len */
@Component({
  selector: 'cdg-config-edit',
  templateUrl: './config-graph-editor.component.html',
  styleUrls: ['./config-graph-editor.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [dropdownPanel],
})
export class ConfigGraphEditorComponent implements OnDestroy, ChangesComponent {
  private unsubscribe$ = new Subject();
  private contextMenuCoords$ = new ReplaySubject<Anchor>(1);

  @ViewChild('warningIcon', { static: true }) warning: TemplateRef<{ $implicit: MeterConfig }>;
  @ViewChild('infoIcon', { static: true }) info: TemplateRef<{ $implicit: MeterConfig }>;
  @ViewChild('nodeContextMenu') nodeContextMenu: TemplateRef<PointOverlayContext<MeterConfig>>;

  private options$ = combineLatest([
    this.store.pipe(select(DataSelectors.measures.getListItems)),
    this.store.pipe(select(DataSelectors.meters.getSortedByName)),
    this.store.pipe(select(ConfigEditorNodeDialogSelectors.getOutputMode)),
    this.store.pipe(select(DataSelectors.constants.getList)),
    this.store.pipe(select(ConfigEditorNodeDialogSelectors.getFieldIsConstant)),
    this.store.pipe(select(ConfigEditorNodeDialogSelectors.getSelectedBaseDimensionality)),
  ]).pipe(
    map(([measures, meters, outputMode, constants, constantsFields, baseDimensionality]) => ({
      measures,
      meters,
      outputMode,
      constants,
      constantsFields,
      baseDimensionality,
    })),
  );

  readonly meterConfigType = MeterConfigType;

  saving$ = this.store.pipe(select(ConfigEditorSelectors.getIsSaving));
  undoEnabled$ = this.store.pipe(select(ConfigEditorSelectors.getUndoEnabled));
  redoEnabled$ = this.store.pipe(select(ConfigEditorSelectors.getRedoEnabled));
  undosCountLabel$ = this.store.pipe(select(ConfigEditorSelectors.getUndosCount));
  hasNoUndos$ = this.store.pipe(
    select(ConfigEditorSelectors.getUndosCount),
    map((count) => count <= 0),
  );
  redosCountLabel$ = this.store.pipe(select(ConfigEditorSelectors.getRedosCount));
  hasNoRedos$ = this.store.pipe(
    select(ConfigEditorSelectors.getRedosCount),
    map((count) => count <= 0),
  );
  meterName$ = this.store.pipe(
    select(fromMeterManagement.getSelectedMeterNormalized),
    map((meter) => meter?.name),
  );
  isDirty$ = this.store.pipe(
    select(ConfigEditorSelectors.getChangesetIds),
    map((ids) => ids.length > 0),
  );
  configsByCategory$: Observable<{ configs: ReadonlyArray<MeterConfigMeta>; name: string }[]> = this.store.pipe(
    select(MeterMgmtDataSelectors.getConfigTypesByCategory),
  );

  graphData$ = this.store.pipe(
    select(fromMeterManagement.getMeterConfigsGraphLayout),
    switchMap((data) =>
      this.layoutService.generateLayout(data, {
        sourceNodeTypes: [MeterConfigType.Historian, MeterConfigType.SourceMeter],
        sinkNodeTypes: [MeterConfigType.VirtualMeter],
        nodeLayout: { labelHeight: 40, portHeight: 20, descriptionHeight: 30 },
      }),
    ),
    retryWhen((errors$) =>
      errors$.pipe(
        withLatestFrom(this.store.pipe(select(ConfigEditorSelectors.getChangesetIds))),
        tap(([error, changes]) =>
          this.store.dispatch(
            MeterMgmtActions.configEditor.generateLayoutFailed({
              error: error?.message,
              hasChanges: changes.length > 0,
            }),
          ),
        ),
        mergeMap(([error, changes]) => (changes.length ? of(true) : throwError(error))),
        delay(100),
      ),
    ),
  );

  readonly configBreadcrumbs$: Observable<readonly MeterNormalized[]> = this.store.pipe(
    select(ConfigEditorSelectors.getNavigationHistory),
  );

  nodeIcons$ = combineLatest([
    this.graphData$.pipe(map(({ nodes }) => nodes)),
    this.store.pipe(select(ConfigEditorSelectors.getCurrentTestResults)),
  ]).pipe(
    map(([meterConfigs, testResults]) => meterConfigs
        .map((config) => {
          const testResult = testResults.filter(hasId(config.id));
          return { config, testResult };
        })
        .filter(({ testResult }) => testResult.length > 0 || testResult[0]?.warnings?.length > 0)
        .map(({ config, testResult }) => ({
          node: config,
          context: <TestResultContext>{
            testData: testResult[0],
          },
          icon: testResult[0]?.warnings?.length <= 0 ? this.info : this.warning,
          hasEvents: true,
        }))),
  );

  readonly resize$ = this.store.pipe(select(fromLayout.getShowSidenav));

  nodeConnectionRules = [alwaysFalse];
  portConnectionRules: readonly PortConnectionRule<MeterConfigPort>[] = [not(sameNode), inputToOutput];
  titleResolver: TextResolver<{ metadata: { label: string }; type: string }> = (config) =>
    config?.metadata?.label ?? config.type;
  descriptionResolver: TextResolver<{ label: string }> = ({ label }) => label;

  ngOnDestroy(): void {
    this.store.dispatch(MeterMgmtActions.configEditor.editorClosed());
    this.unsubscribe$.next();
    this.unsubscribe$.complete();
    this.contextMenuCoords$.complete();
  }

  onGoBack() {
    this.store.dispatch(MeterMgmtActions.configEditor.navigateBack());
  }

  onNodeSelected(event: { node: MeterConfig; anchor: Anchor }) {
    const { node, anchor } = event;
    const dialogConfig = {
      title: `Edit config`,
      formProcessor: this.getFormProcessor(node.metadata),
      removeOnSave: fieldsToRemoveOnSave(node.metadata),
      metadata: node.metadata,
      anchor,
    } as DialogContext;
    this.openNodeDialog(dialogConfig, node)
      .pipe(
        map((config) =>
          node.metadata.dynamic
            ? MeterMgmtActions.configEditor.loadEditConfig({
                oldConfig: node,
                newConfig: config,
              })
            : MeterMgmtActions.configEditor.updateConfig({
                config: { ...diffObject(config, node), id: node.id },
              }),
        ),
      )
      .subscribe(this.store);
  }

  onCreateNewConfig(meta: MeterConfigMeta) {
    const dialogConfig = {
      title: `Create config`,
      formProcessor: this.getFormProcessor(meta),
      removeOnSave: fieldsToRemoveOnSave(meta),
      metadata: meta,
    } as DialogContext;
    this.openNodeDialog(dialogConfig)
      .pipe(
        map((config) =>
          meta.dynamic
            ? MeterMgmtActions.configEditor.loadCreateConfig({ config, meta })
            : MeterMgmtActions.configEditor.loadCreateConfigSuccess({ config, meta }),
        ),
      )
      .subscribe(this.store);
  }

  onNodeDeleted(config: MeterConfig) {
    this.store.dispatch(MeterMgmtActions.configEditor.deleteMeterConfig({ config }));
  }

  onConnectionDelete(connection: [Id, Id, Id, Id]) {
    this.store.dispatch(MeterMgmtActions.configEditor.deleteConnection({ connection }));
  }

  onConnectionAdded(connection: { connection: Connection; connectedPort?: MeterConfigPort }) {
    this.store.dispatch(MeterMgmtActions.configEditor.addConnection(connection));
  }

  onResetChanges() {
    this.store.dispatch(MeterMgmtActions.configEditor.resetChanges());
  }

  onSaveChanges() {
    this.store
      .pipe(
        select(ConfigEditorSelectors.getCleanChangesetEntities),
        withLatestFrom(
          this.store.pipe(select(MetersListSelectors.getSelectedId)),
          this.store.pipe(select(fromMeterManagement.getMeterConfigsData)),
          this.store.pipe(select(ConfigEditorSelectors.getConnectedPortId)),
        ),
        take(1),
        map(([changes, meterId, originalEntities, connectedPort]) =>
          squashChanges(changes, meterId, originalEntities, connectedPort),
        ),
        map(serializeChanges),
        map((changes) => MeterMgmtActions.configEditor.saveChanges({ changes })),
      )
      .subscribe(this.store);
  }

  onUndoChange() {
    this.store.dispatch(MeterMgmtActions.configEditor.undoChange());
  }

  onRedoChange() {
    this.store.dispatch(MeterMgmtActions.configEditor.redoChange());
  }

  private openNodeDialog(dialogConfig: DialogContext, meterConfig?: MeterConfig) {
    const { save$, cancel$, componentRef$ } = this.globalOverlay.create<DialogContext, any, MeterConfigComponent>(
      dialogConfig,
      MeterConfigComponent,
      dialogConfig.anchor,
      {
        disableBackdropClick: true,
        disableCancel: false,
      },
    );

    const HELP_COMPONENTS: Partial<Dict<ComponentType<ClosableDialog>, MeterConfigType>> = {
      [MeterConfigType.GenericParser]: MeterModelParserHelpComponent,
    };

    componentRef$
      .pipe(
        take(1),
        switchMap(({ instance }) => instance.helpClicked.pipe(takeUntil(merge(save$, cancel$)))),
        map(() => HELP_COMPONENTS[dialogConfig.metadata.operation]),
      )
      .subscribe((component) => {
        this.globalOverlay.create(null, component);
      });

    this.options$
      .pipe(
        withLatestFrom(this.autoNameService.getName(dialogConfig.metadata.type)),
        takeUntil(merge(save$, cancel$)),
        switchMap(([options, defaultName]) =>
          componentRef$.pipe(
            takeUntil(merge(save$, cancel$)),
            map((componentRef) => ({ options, defaultName, componentRef })),
          ),
        ),
      )
      .subscribe(({ componentRef, options, defaultName }) => {
        componentRef.instance.fields = getFormFields({
          ...options,
          metadata: dialogConfig.metadata,
          config: meterConfig,
          defaultName,
        });
        componentRef.instance.hasHelp = dialogConfig.metadata.operation === MeterConfigType.GenericParser;
      });

    return save$.pipe(takeUntil(this.unsubscribe$), take(1));
  }

  private getFormProcessor(metadata: MeterConfigMeta) {
    const formProcessors: Partial<Dict<FormProcessor, MeterConfigType>> = {
      [MeterConfigType.Historian]: (form) => {
        const tableNameField = form.get('tableName') as FormControl;
        tableNameField.setAsyncValidators(createTableNameValidator(this.tableNameValidatorService));
      },
      [MeterConfigType.SourceConstant]: (form, close$) => {
        form.setAsyncValidators(createDatesValidator(this.datesValidatorService));
        this.setupConstantField({
          form,
          close$,
          valueField: 'value',
          constantField: 'constant',
          useConstantField: 'useConstant',
          measureField: 'measureId',
        });
        const isConstantControl = form.get('useConstant') as FormControl;

        this.store
          .pipe(select(ConfigEditorNodeDialogSelectors.getAvailableConstants), takeUntil(close$))
          .subscribe((availableConstants) => {
            if (!availableConstants.length) {
              isConstantControl.setValue(false);
            }
          });
      },
      [MeterConfigType.ScalarOperator]: (form, close$) => {
        form.setAsyncValidators(createDatesValidator(this.datesValidatorService));
        this.setupConstantField({
          close$,
          form,
          valueField: 'scalar',
          constantField: 'constant',
          useConstantField: 'useConstant',
          measureField: 'measureId',
        });

        const isConstantControl = form.get('useConstant') as FormControl;

        this.store
          .pipe(select(ConfigEditorNodeDialogSelectors.getAvailableConstants), takeUntil(close$))
          .subscribe((availableConstants) => {
            if (!availableConstants.length) {
              isConstantControl.setValue(false);
            }
          });
      },
      [MeterConfigType.GenericParser]: (form) => {
        const formulaField = form.get('formula') as FormControl;
        formulaField.setAsyncValidators(createParserValidator(this.parserValidatorService));
      },
      [MeterConfigType.Limit]: (form) => {
        form.setAsyncValidators(createLimitsValidator(this.limitsValidatorService));
      },
      [MeterConfigType.Select]: (form, close$) => {
        const outputModeControl = form.get('outputMode') as FormControl;
        outputModeControl.valueChanges
          .pipe(
            takeUntil(close$),
            startWith(<string>outputModeControl.value),
            map((outputMode) => MeterMgmtActions.configEditorNodeDialog.selectOutputMode({ outputMode })),
          )
          .subscribe(this.store);
      },
    };

    const { operation: type, constants } = metadata;

    const generalProcessor: FormProcessor = (form, close$) => {
      if (isEmpty(constants)) {
        return;
      }
      Object.keys(constants).forEach((fieldKey) =>
        this.setupConstantField({
          form,
          close$,
          useConstantField: getUseConstantFieldKey(fieldKey),
          constantField: getConstantFieldKey(fieldKey),
          valueField: fieldKey,
        }),
      );
      close$.pipe(map(() => MeterMgmtActions.configEditorNodeDialog.reset())).subscribe(this.store);
    };

    return ((form, close$, host) => {
      if (formProcessors[type]) {
        formProcessors[type](form, close$, host);
      }
      generalProcessor(form, close$, host);
    }) as FormProcessor;
  }

  private setupConstantField(config: {
    measureField?: string;
    useConstantField: string;
    valueField: string;
    constantField: string;
    form: FormGroup;
    close$: Observable<any>;
  }) {
    const { form, close$, valueField, constantField, measureField, useConstantField } = config;

    const measureIdControl = form.get(measureField) as FormControl;
    const isConstantControl = form.get(useConstantField) as FormControl;
    const valueControl = form.get(valueField) as FormControl;
    const constantControl = form.get(constantField) as FormControl;
    const useConstant$ = isConstantControl.valueChanges.pipe(startWith(<boolean>isConstantControl.value));

    useConstant$
      .pipe(
        map((isConstant) => MeterMgmtActions.configEditorNodeDialog.setIsConstant({ isConstant, field: valueField })),
        takeUntil(close$),
      )
      .subscribe(this.store);

    useConstant$.pipe(takeUntil(close$)).subscribe((isConstant) => {
      if (isConstant) {
        valueControl.setValue(null);
        valueControl.clearValidators();
        constantControl.setValidators(Validators.required);
      } else {
        constantControl.clearValidators();
        constantControl.setValue(null);
        valueControl.setValidators(Validators.required);
      }
      constantControl.updateValueAndValidity();
      valueControl.updateValueAndValidity();
    });

    if (measureIdControl != null) {
      measureIdControl.valueChanges
        .pipe(
          startWith(<Id>measureIdControl.value),
          map((measure) => MeterMgmtActions.configEditorNodeDialog.selectMeasure({ measure })),
          takeUntil(close$),
        )
        .subscribe(this.store);
    }
  }

  isDirty(): boolean | Observable<boolean> {
    return this.store.pipe(select(ConfigEditorSelectors.getUndoEnabled));
  }

  onRunTest() {
    this.store
      .pipe(
        select(fromMeterManagement.getSelectedMeterNormalized),
        map(pluckId),
        map((meterId) => MeterMgmtActions.configEditor.runTests({ meterId })),
        take(1),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }

  onTestResult(anchor: CdkOverlayOrigin, result: TestResultContext) {
    this.connectedOverlay
      .create(anchor, this.viewContainerRef, result, TestResultComponent)
      .onSave()
      .pipe(
        filter(({ openMeterIdConfigs }) => openMeterIdConfigs != null),
        map(({ openMeterIdConfigs }) => openMeterIdConfigs),
        map((id) => MeterMgmtActions.configEditor.openConfigGraphEditor({ id })),
      )
      .subscribe(this.store);
  }

  onNodeContextMenu(event: { anchor: Anchor; node: MeterConfig }) {
    if (event == null || event.node.type === MeterConfigType.VirtualMeter) {
      return;
    }

    const { node, anchor } = event;
    this.contextMenuCoords$.next(anchor);
    this.pointOverlay.open<MeterConfig>(anchor, node, this.nodeContextMenu, this.viewContainerRef);
  }

  onNavigateToSourceMeter(config: MeterConfig) {
    if (config.type === MeterConfigType.SourceMeter) {
      this.onNavigateToMeter(config.sourceMeterId);
    }
  }

  onNavigateToMeter(id: Id) {
    this.store.dispatch(MeterMgmtActions.configEditor.openConfigGraphEditor({ id }));
  }

  constructor(
    private store: Store<fromMeterManagement.State>,
    private layoutService: GraphLayoutService<InputPortNormalized, OutputPortNormalized, MeterConfig>,
    private route: ActivatedRoute,
    private globalOverlay: OverlayGlobalService,
    private connectedOverlay: OverlayConnectedService,
    private pointOverlay: OverlayPointService,
    private datesValidatorService: DatesValidatorService,
    private limitsValidatorService: LimitsValidatorService,
    private parserValidatorService: ParserValidatorService,
    private tableNameValidatorService: TableNameValidatorService,
    private autoNameService: AutonameService,
    private viewContainerRef: ViewContainerRef,
  ) {
    this.route.paramMap
      .pipe(
        map((params) => params.get('id')),
        map((id) => MeterMgmtActions.configEditor.openConfigGraphEditorSuccess({ id })),
        takeUntil(this.unsubscribe$),
      )
      .subscribe(this.store);
  }
}
